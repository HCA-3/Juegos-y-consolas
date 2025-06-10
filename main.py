from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
import psycopg2
import psycopg2.extras
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Cargar variables de entorno
load_dotenv()

app = FastAPI(
    title="API de Videojuegos",
    description="Sistema completo con búsqueda, gestión y comparación de juegos, consolas y accesorios"
)

# --- Configuración de directorios y plantillas ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# UPLOADS_DIR ya no se usa para almacenamiento persistente de imágenes
# os.makedirs(UPLOADS_DIR, exist_ok=True) # Ya no es necesario crear esta carpeta si las imágenes van a Cloudinary

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- URL de Conexión a PostgreSQL (desde .env) ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("La variable de entorno DATABASE_URL no está configurada.")

# --- Configuración de Cloudinary ---
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

if not all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
    raise ValueError("Las variables de entorno de Cloudinary no están configuradas correctamente. Asegúrate de tener CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY y CLOUDINARY_API_SECRET.")

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True # Usar HTTPS
)

# --- Modelos Pydantic (sin cambios) ---
class JuegoBase(BaseModel):
    nombre: str
    genero: str
    año: Optional[int] = None
    desarrollador: Optional[str] = None

class ConsolaBase(BaseModel):
    nombre: str
    fabricante: str
    año_lanzamiento: Optional[int] = None

class AccesorioBase(BaseModel):
    nombre: str
    tipo: str
    compatible_con: Optional[str] = None

class ComparacionBase(BaseModel):
    nombre: str
    juego_id: int
    consola_id: int
    accesorio_id: Optional[int] = None
    notas: Optional[str] = None

class HistorialItem(BaseModel):
    id: int
    fecha: datetime
    accion: str
    detalles: str
    tipo_objeto: Optional[str] = None
    objeto_id: Optional[int] = None

# --- Función de conexión a la base de datos ---
def get_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")

# --- Funciones de Cloudinary ---
async def upload_file_to_cloudinary(file: UploadFile, folder: str):
    """Sube un archivo a Cloudinary y devuelve su URL pública."""
    try:
        # Asegúrate de que el puntero del archivo esté al principio
        await file.seek(0)
        
        public_id_with_folder = f"{folder}/{uuid.uuid4()}" 
        
        upload_result = cloudinary.uploader.upload(file.file, 
                                                 public_id=public_id_with_folder,
                                                 folder=folder, 
                                                 resource_type="auto" 
                                                )
        
        return upload_result['secure_url']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir archivo a Cloudinary: {str(e)}")

def get_public_id_from_cloudinary_url(image_url: str) -> Optional[str]:
    """Extrae el public_id de una URL de Cloudinary."""
    try:
        parts = image_url.split('/')
        try:
            upload_index = parts.index('upload')
        except ValueError:
            return None 
        
        public_id_parts = []
        for i in range(upload_index + 1, len(parts)):
            if not parts[i].startswith('v') or not parts[i][1:].isdigit():
                public_id_parts.append(parts[i])
        
        if not public_id_parts:
            return None 
        
        last_part = public_id_parts[-1]
        if '.' in last_part:
            public_id_parts[-1] = last_part.rsplit('.', 1)[0] 
        
        return '/'.join(public_id_parts)
        
    except Exception as e:
        print(f"Error al parsear URL de Cloudinary: {e}")
        return None

def delete_file_from_cloudinary(image_url: str):
    """Elimina un archivo de Cloudinary dada su URL pública."""
    if not image_url:
        return 

    public_id = get_public_id_from_cloudinary_url(image_url)
    if not public_id:
        print(f"Advertencia: No se pudo obtener el public_id de la URL para eliminar: {image_url}")
        return
        
    try:
        cloudinary.uploader.destroy(public_id, resource_type="image")
    except Exception as e:
        print(f"Error al eliminar archivo de Cloudinary {public_id} ({image_url}): {str(e)}")

# --- Función de registro de historial (sin cambios) ---
def registrar_historial(accion: str, detalles: str, tipo_objeto: Optional[str] = None, objeto_id: Optional[int] = None):
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO historial (fecha, accion, detalles, tipo_objeto, objeto_id)
            VALUES (NOW(), %s, %s, %s, %s)
            """,
            (accion, detalles, tipo_objeto, objeto_id),
        )
        conn.commit()
    except Exception as e:
        print(f"Error al registrar historial: {e}")
        conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --- Rutas para servir archivos estáticos y plantillas HTML (sin cambios) ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/consolas", response_class=HTMLResponse)
async def read_consolas(request: Request):
    return templates.TemplateResponse("consolas.html", {"request": request})

@app.get("/accesorios", response_class=HTMLResponse)
async def read_accesorios(request: Request):
    return templates.TemplateResponse("accesorios.html", {"request": request})

@app.get("/comparaciones", response_class=HTMLResponse)
async def read_comparaciones(request: Request):
    return templates.TemplateResponse("comparaciones.html", {"request": request})

@app.get("/historial", response_class=HTMLResponse)
async def read_historial(request: Request, clave: str = Query(...)):
    if clave != "0000": # Cambia "0000" por una clave más segura en producción
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    historial = []
    try:
        cursor.execute("SELECT * FROM historial ORDER BY fecha DESC LIMIT 50")
        historial = cursor.fetchall()
        return templates.TemplateResponse("historial.html", {"request": request, "historial": historial})
    finally:
        cursor.close()
        conn.close()

# --- API de Juegos ---
@app.get("/api/juegos/", response_class=JSONResponse)
async def obtener_juegos(
    q: Optional[str] = Query(None, description="Término de búsqueda para juegos"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        if q:
            cursor.execute(
                """
                SELECT id, nombre, genero, año, desarrollador, imagen
                FROM juegos
                WHERE nombre ILIKE %s OR genero ILIKE %s OR desarrollador ILIKE %s
                ORDER BY nombre
                OFFSET %s LIMIT %s
                """,
                (f"%{q}%", f"%{q}%", f"%{q}%", skip, limit),
            )
        else:
            cursor.execute(
                """
                SELECT id, nombre, genero, año, desarrollador, imagen
                FROM juegos
                ORDER BY nombre
                OFFSET %s LIMIT %s
                """,
                (skip, limit),
            )
        juegos = cursor.fetchall()
        return [dict(juego) for juego in juegos]
    finally:
        cursor.close()
        conn.close()

@app.post("/api/juegos/", response_class=JSONResponse)
async def crear_juego(
    nombre: str = Form(...),
    genero: str = Form(...),
    año: Optional[int] = Form(None),
    desarrollador: Optional[str] = Form(None),
    imagen: Optional[UploadFile] = File(None)
):
    conn = get_db()
    cursor = conn.cursor()
    imagen_url = None
    try:
        if imagen and imagen.filename:
            imagen_url = await upload_file_to_cloudinary(imagen, "juegos") 
            
        cursor.execute(
            """
            INSERT INTO juegos (nombre, genero, año, desarrollador, imagen)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
            """,
            (nombre, genero, año, desarrollador, imagen_url), 
        )
        juego_id = cursor.fetchone()[0]
        conn.commit()
        
        registrar_historial("Creación", f"Juego creado: {nombre}", "juego", juego_id)
        
        return {"message": "Juego creado con éxito", "id": juego_id, "imagen_url": imagen_url}
    except Exception as e:
        conn.rollback()
        if imagen_url:
            delete_file_from_cloudinary(imagen_url)
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.put("/api/juegos/{juego_id}", response_class=JSONResponse)
async def actualizar_juego(
    juego_id: int,
    nombre: str = Form(...),
    genero: str = Form(...),
    año: Optional[int] = Form(None),
    desarrollador: Optional[str] = Form(None),
    imagen: Optional[UploadFile] = File(None), 
    mantener_imagen_existente: bool = Form(False) 
):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    old_imagen_url = None
    new_imagen_url = None 
    final_imagen_url = None 

    try:
        cursor.execute("SELECT nombre, imagen FROM juegos WHERE id = %s", (juego_id,))
        old_juego_data = cursor.fetchone()
        if not old_juego_data:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        
        old_imagen_url = old_juego_data['imagen']
        
        if imagen and imagen.filename: 
            new_imagen_url = await upload_file_to_cloudinary(imagen, "juegos")
            final_imagen_url = new_imagen_url
            if old_imagen_url:
                delete_file_from_cloudinary(old_imagen_url)
        elif mantener_imagen_existente: 
            final_imagen_url = old_imagen_url
        else: 
            if old_imagen_url:
                delete_file_from_cloudinary(old_imagen_url)
            final_imagen_url = None 

        cursor.execute(
            """
            UPDATE juegos
            SET nombre = %s, genero = %s, año = %s, desarrollador = %s, imagen = %s
            WHERE id = %s
            """,
            (nombre, genero, año, desarrollador, final_imagen_url, juego_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        
        conn.commit()
        
        registrar_historial("Actualización", f"Juego actualizado: {nombre}", "juego", juego_id)
        
        return {"message": "Juego actualizado con éxito", "imagen_url": final_imagen_url}
    except Exception as e:
        conn.rollback()
        if new_imagen_url and new_imagen_url != old_imagen_url: 
             delete_file_from_cloudinary(new_imagen_url)
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/juegos/{juego_id}", response_class=JSONResponse)
async def eliminar_juego(juego_id: int):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    old_imagen_url = None
    try:
        cursor.execute("SELECT nombre, imagen FROM juegos WHERE id = %s", (juego_id,))
        datos = cursor.fetchone()
        if not datos:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        
        nombre_juego = datos['nombre']
        old_imagen_url = datos['imagen']

        cursor.execute("DELETE FROM juegos WHERE id = %s", (juego_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        
        conn.commit()
        
        if old_imagen_url:
            delete_file_from_cloudinary(old_imagen_url)
            
        registrar_historial("Eliminación", f"Juego eliminado: {nombre_juego}", "juego", juego_id)
        
        return {"message": "Juego eliminado con éxito"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# --- API de Consolas ---
@app.get("/api/consolas/", response_class=JSONResponse)
async def obtener_consolas(
    q: Optional[str] = Query(None, description="Término de búsqueda para consolas"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        if q:
            cursor.execute(
                """
                SELECT id, nombre, fabricante, año_lanzamiento, imagen
                FROM consolas
                WHERE nombre ILIKE %s OR fabricante ILIKE %s
                ORDER BY nombre
                OFFSET %s LIMIT %s
                """,
                (f"%{q}%", f"%{q}%", skip, limit),
            )
        else:
            cursor.execute(
                """
                SELECT id, nombre, fabricante, año_lanzamiento, imagen
                FROM consolas
                ORDER BY nombre
                OFFSET %s LIMIT %s
                """,
                (skip, limit),
            )
        consolas = cursor.fetchall()
        return [dict(consola) for consola in consolas]
    finally:
        cursor.close()
        conn.close()

@app.post("/api/consolas/", response_class=JSONResponse)
async def crear_consola(
    nombre: str = Form(...),
    fabricante: str = Form(...),
    año_lanzamiento: Optional[int] = Form(None),
    imagen: Optional[UploadFile] = File(None)
):
    conn = get_db()
    cursor = conn.cursor()
    imagen_url = None
    try:
        if imagen and imagen.filename:
            imagen_url = await upload_file_to_cloudinary(imagen, "consolas")
            
        cursor.execute(
            """
            INSERT INTO consolas (nombre, fabricante, año_lanzamiento, imagen)
            VALUES (%s, %s, %s, %s) RETURNING id
            """,
            (nombre, fabricante, año_lanzamiento, imagen_url),
        )
        consola_id = cursor.fetchone()[0]
        conn.commit()
        
        registrar_historial("Creación", f"Consola creada: {nombre}", "consola", consola_id)
        
        return {"message": "Consola creada con éxito", "id": consola_id, "imagen_url": imagen_url}
    except Exception as e:
        conn.rollback()
        if imagen_url:
            delete_file_from_cloudinary(imagen_url)
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.put("/api/consolas/{consola_id}", response_class=JSONResponse)
async def actualizar_consola(
    consola_id: int,
    nombre: str = Form(...),
    fabricante: str = Form(...),
    año_lanzamiento: Optional[int] = Form(None),
    imagen: Optional[UploadFile] = File(None),
    mantener_imagen_existente: bool = Form(False)
):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    old_imagen_url = None
    new_imagen_url = None
    final_imagen_url = None
    try:
        cursor.execute("SELECT nombre, imagen FROM consolas WHERE id = %s", (consola_id,))
        old_consola_data = cursor.fetchone()
        if not old_consola_data:
            raise HTTPException(status_code=404, detail="Consola no encontrada")
        
        old_imagen_url = old_consola_data['imagen']

        if imagen and imagen.filename:
            new_imagen_url = await upload_file_to_cloudinary(imagen, "consolas")
            final_imagen_url = new_imagen_url
            if old_imagen_url:
                delete_file_from_cloudinary(old_imagen_url)
        elif mantener_imagen_existente:
            final_imagen_url = old_imagen_url
        else:
            if old_imagen_url:
                delete_file_from_cloudinary(old_imagen_url)
            final_imagen_url = None

        cursor.execute(
            """
            UPDATE consolas
            SET nombre = %s, fabricante = %s, año_lanzamiento = %s, imagen = %s
            WHERE id = %s
            """,
            (nombre, fabricante, año_lanzamiento, final_imagen_url, consola_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Consola no encontrada")
        
        conn.commit()
        
        registrar_historial("Actualización", f"Consola actualizada: {nombre}", "consola", consola_id)
        
        return {"message": "Consola actualizada con éxito", "imagen_url": final_imagen_url}
    except Exception as e:
        conn.rollback()
        if new_imagen_url and new_imagen_url != old_imagen_url:
             delete_file_from_cloudinary(new_imagen_url)
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/consolas/{consola_id}", response_class=JSONResponse)
async def eliminar_consola(consola_id: int):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    old_imagen_url = None
    try:
        cursor.execute("SELECT nombre, imagen FROM consolas WHERE id = %s", (consola_id,))
        datos = cursor.fetchone()
        if not datos:
            raise HTTPException(status_code=404, detail="Consola no encontrada")
        
        nombre_consola = datos['nombre']
        old_imagen_url = datos['imagen']

        cursor.execute("DELETE FROM consolas WHERE id = %s", (consola_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Consola no encontrada")
        
        conn.commit()
        
        if old_imagen_url:
            delete_file_from_cloudinary(old_imagen_url)
            
        registrar_historial("Eliminación", f"Consola eliminada: {nombre_consola}", "consola", consola_id)
        
        return {"message": "Consola eliminada con éxito"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# --- API de Accesorios ---
@app.get("/api/accesorios/", response_class=JSONResponse)
async def obtener_accesorios(
    q: Optional[str] = Query(None, description="Término de búsqueda para accesorios"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        if q:
            cursor.execute(
                """
                SELECT id, nombre, tipo, compatible_con, imagen
                FROM accesorios
                WHERE nombre ILIKE %s OR tipo ILIKE %s OR compatible_con ILIKE %s
                ORDER BY nombre
                OFFSET %s LIMIT %s
                """,
                (f"%{q}%", f"%{q}%", f"%{q}%", skip, limit),
            )
        else:
            cursor.execute(
                """
                SELECT id, nombre, tipo, compatible_con, imagen
                FROM accesorios
                ORDER BY nombre
                OFFSET %s LIMIT %s
                """,
                (skip, limit),
            )
        accesorios = cursor.fetchall()
        return [dict(accesorio) for accesorio in accesorios]
    finally:
        cursor.close()
        conn.close()

@app.post("/api/accesorios/", response_class=JSONResponse)
async def crear_accesorio(
    nombre: str = Form(...),
    tipo: str = Form(...),
    compatible_con: Optional[str] = Form(None),
    imagen: Optional[UploadFile] = File(None)
):
    conn = get_db()
    cursor = conn.cursor()
    imagen_url = None
    try:
        if imagen and imagen.filename:
            imagen_url = await upload_file_to_cloudinary(imagen, "accesorios")
            
        cursor.execute(
            """
            INSERT INTO accesorios (nombre, tipo, compatible_con, imagen)
            VALUES (%s, %s, %s, %s) RETURNING id
            """,
            (nombre, tipo, compatible_con, imagen_url),
        )
        accesorio_id = cursor.fetchone()[0]
        conn.commit()
        
        registrar_historial("Creación", f"Accesorio creado: {nombre}", "accesorio", accesorio_id)
        
        return {"message": "Accesorio creado con éxito", "id": accesorio_id, "imagen_url": imagen_url}
    except Exception as e:
        conn.rollback()
        if imagen_url:
            delete_file_from_cloudinary(imagen_url)
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.put("/api/accesorios/{accesorio_id}", response_class=JSONResponse)
async def actualizar_accesorio(
    accesorio_id: int,
    nombre: str = Form(...),
    tipo: str = Form(...),
    compatible_con: Optional[str] = Form(None),
    imagen: Optional[UploadFile] = File(None),
    mantener_imagen_existente: bool = Form(False)
):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    old_imagen_url = None
    new_imagen_url = None
    final_imagen_url = None
    try:
        cursor.execute("SELECT nombre, imagen FROM accesorios WHERE id = %s", (accesorio_id,))
        old_accesorio_data = cursor.fetchone()
        if not old_accesorio_data:
            raise HTTPException(status_code=404, detail="Accesorio no encontrado")
        
        old_imagen_url = old_accesorio_data['imagen']

        if imagen and imagen.filename:
            new_imagen_url = await upload_file_to_cloudinary(imagen, "accesorios")
            final_imagen_url = new_imagen_url
            if old_imagen_url:
                delete_file_from_cloudinary(old_imagen_url)
        elif mantener_imagen_existente:
            final_imagen_url = old_imagen_url
        else:
            if old_imagen_url:
                delete_file_from_cloudinary(old_imagen_url)
            final_imagen_url = None

        cursor.execute(
            """
            UPDATE accesorios
            SET nombre = %s, tipo = %s, compatible_con = %s, imagen = %s
            WHERE id = %s
            """,
            (nombre, tipo, compatible_con, final_imagen_url, accesorio_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Accesorio no encontrado")
        
        conn.commit()
        
        registrar_historial("Actualización", f"Accesorio actualizado: {nombre}", "accesorio", accesorio_id)
        
        return {"message": "Accesorio actualizado con éxito", "imagen_url": final_imagen_url}
    except Exception as e:
        conn.rollback()
        if new_imagen_url and new_imagen_url != old_imagen_url:
             delete_file_from_cloudinary(new_imagen_url)
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/accesorios/{accesorio_id}", response_class=JSONResponse)
async def eliminar_accesorio(accesorio_id: int):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    old_imagen_url = None
    try:
        cursor.execute("SELECT nombre, imagen FROM accesorios WHERE id = %s", (accesorio_id,))
        datos = cursor.fetchone()
        if not datos:
            raise HTTPException(status_code=404, detail="Accesorio no encontrado")
        
        nombre_accesorio = datos['nombre']
        old_imagen_url = datos['imagen']

        cursor.execute("DELETE FROM accesorios WHERE id = %s", (accesorio_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Accesorio no encontrado")
        
        conn.commit()
        
        if old_imagen_url:
            delete_file_from_cloudinary(old_imagen_url)
            
        registrar_historial("Eliminación", f"Accesorio eliminado: {nombre_accesorio}", "accesorio", accesorio_id)
        
        return {"message": "Accesorio eliminado con éxito"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# --- API de Comparaciones ---
@app.get("/api/comparaciones/", response_class=JSONResponse)
async def obtener_comparaciones(
    q: Optional[str] = Query(None, description="Término de búsqueda para comparaciones"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        base_query = """
            SELECT
                c.id, c.nombre, c.notas, c.juego_id, c.consola_id, c.accesorio_id,
                j.nombre AS juego_nombre, j.genero AS juego_genero, j.año AS juego_año, j.desarrollador AS juego_desarrollador, j.imagen AS juego_imagen,
                con.nombre AS consola_nombre, con.fabricante AS consola_fabricante, con.año_lanzamiento AS consola_año_lanzamiento, con.imagen AS consola_imagen,
                acc.nombre AS accesorio_nombre, acc.tipo AS accesorio_tipo, acc.compatible_con AS accesorio_compatible_con, acc.imagen AS accesorio_imagen
            FROM comparaciones c
            JOIN juegos j ON c.juego_id = j.id
            JOIN consolas con ON c.consola_id = con.id
            LEFT JOIN accesorios acc ON c.accesorio_id = acc.id
        """
        
        if q:
            cursor.execute(
                base_query + """
                WHERE c.nombre ILIKE %s OR j.nombre ILIKE %s OR con.nombre ILIKE %s OR acc.nombre ILIKE %s
                ORDER BY c.nombre
                OFFSET %s LIMIT %s
                """,
                (f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%", skip, limit),
            )
        else:
            cursor.execute(
                base_query + """
                ORDER BY c.nombre
                OFFSET %s LIMIT %s
                """,
                (skip, limit),
            )
        comparaciones = cursor.fetchall()
        return [dict(comp) for comp in comparaciones]
    finally:
        cursor.close()
        conn.close()

@app.get("/api/comparaciones/{comparacion_id}", response_class=JSONResponse)
async def obtener_comparacion(comparacion_id: int):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute(
            """
            SELECT
                c.id, c.nombre, c.notas, c.juego_id, c.consola_id, c.accesorio_id,
                j.nombre AS juego_nombre, j.genero AS juego_genero, j.año AS juego_año, j.desarrollador AS juego_desarrollador, j.imagen AS juego_imagen,
                con.nombre AS consola_nombre, con.fabricante AS consola_fabricante, con.año_lanzamiento AS consola_año_lanzamiento, con.imagen AS consola_imagen,
                acc.nombre AS accesorio_nombre, acc.tipo AS accesorio_tipo, acc.compatible_con AS accesorio_compatible_con, acc.imagen AS accesorio_imagen
            FROM comparaciones c
            JOIN juegos j ON c.juego_id = j.id
            JOIN consolas con ON c.consola_id = con.id
            LEFT JOIN accesorios acc ON c.accesorio_id = acc.id
            WHERE c.id = %s
            """,
            (comparacion_id,),
        )
        comparacion = cursor.fetchone()
        if not comparacion:
            raise HTTPException(status_code=404, detail="Comparación no encontrada")
        return dict(comparacion)
    finally:
        cursor.close()
        conn.close()

@app.post("/api/comparaciones/", response_class=JSONResponse)
async def crear_comparacion(comparacion: ComparacionBase):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO comparaciones (nombre, juego_id, consola_id, accesorio_id, notas)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
            """,
            (
                comparacion.nombre,
                comparacion.juego_id,
                comparacion.consola_id,
                comparacion.accesorio_id,
                comparacion.notas,
            ),
        )
        comparacion_id = cursor.fetchone()[0]
        conn.commit()

        registrar_historial("Creación", f"Comparación creada: {comparacion.nombre}", "comparacion", comparacion_id)

        return {"message": "Comparación creada con éxito", "id": comparacion_id}
    except psycopg2.IntegrityError as e:
        conn.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error de integridad en la base de datos (posiblemente IDs de juego/consola/accesorio inválidos): {e}",
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.put("/api/comparaciones/{comparacion_id}", response_class=JSONResponse)
async def actualizar_comparacion(comparacion_id: int, comparacion: ComparacionBase):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE comparaciones
            SET nombre = %s, juego_id = %s, consola_id = %s, accesorio_id = %s, notas = %s
            WHERE id = %s
            """,
            (
                comparacion.nombre,
                comparacion.juego_id,
                comparacion.consola_id,
                comparacion.accesorio_id,
                comparacion.notas,
                comparacion_id,
            ),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Comparación no encontrada")
        
        conn.commit()

        registrar_historial("Actualización", f"Comparación actualizada: {comparacion.nombre}", "comparacion", comparacion_id)

        return {"message": "Comparación actualizada con éxito"}
    except psycopg2.IntegrityError as e:
        conn.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error de integridad en la base de datos (posiblemente IDs de juego/consola/accesorio inválidos): {e}",
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/comparaciones/{comparacion_id}", response_class=JSONResponse)
async def eliminar_comparacion(comparacion_id: int):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("""
            SELECT c.nombre, j.nombre as juego_nombre, con.nombre as consola_nombre
            FROM comparaciones c
            JOIN juegos j ON c.juego_id = j.id
            JOIN consolas con ON c.consola_id = con.id
            WHERE c.id = %s
        """, (comparacion_id,))
        datos = cursor.fetchone()
        if not datos:
            raise HTTPException(status_code=404, detail="Comparación no encontrada")
            
        cursor.execute("DELETE FROM comparaciones WHERE id = %s", (comparacion_id,))
        
        conn.commit()
        registrar_historial(
            "Eliminación",
            f"Comparación eliminada: {datos['nombre']} ({datos['juego_nombre']} con {datos['consola_nombre']})",
            "comparacion",
            comparacion_id
        )
        return {"message": "Comparación eliminada con éxito"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# --- API de Búsqueda General ---
@app.get("/api/buscar", response_class=JSONResponse)
async def buscar_general(q: str = Query(..., min_length=2), tipo: Optional[str] = Query("all")):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    resultados = {"juegos": [], "consolas": [], "accesorios": []}
    
    search_term = f"%{q}%"

    try:
        if tipo in ["all", "juegos"]:
            cursor.execute(
                """
                SELECT id, nombre, genero, año, desarrollador, imagen FROM juegos
                WHERE nombre ILIKE %s OR genero ILIKE %s OR desarrollador ILIKE %s
                LIMIT 10
                """,
                (search_term, search_term, search_term),
            )
            resultados["juegos"] = [dict(row) for row in cursor.fetchall()]

        if tipo in ["all", "consolas"]:
            cursor.execute(
                """
                SELECT id, nombre, fabricante, año_lanzamiento, imagen FROM consolas
                WHERE nombre ILIKE %s OR fabricante ILIKE %s
                LIMIT 10
                """,
                (search_term, search_term),
            )
            resultados["consolas"] = [dict(row) for row in cursor.fetchall()]

        if tipo in ["all", "accesorios"]:
            cursor.execute(
                """
                SELECT id, nombre, tipo, compatible_con, imagen FROM accesorios
                WHERE nombre ILIKE %s OR tipo ILIKE %s OR compatible_con ILIKE %s
                LIMIT 10
                """,
                (search_term, search_term, search_term),
            )
            resultados["accesorios"] = [dict(row) for row in cursor.fetchall()]

        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la búsqueda: {str(e)}")
    finally:
        cursor.close()
        conn.close()