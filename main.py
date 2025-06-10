from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form, Depends, Query
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

app = FastAPI(
    title="API de Videojuegos",
    description="Sistema completo con búsqueda, gestión y comparación de juegos, consolas y accesorios"
)

# --- Configuración de directorios y plantillas ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- URL de Conexión a PostgreSQL ---
DATABASE_URL = "postgresql://hca3:a5jh8ABfovYdHT17yVw46nc5gYp60u9n@dpg-d13sdjmmcj7s738d7kvg-a/database_juegos_y_accesorios" # 

# --- Modelos Pydantic (sin cambios) ---
class JuegoBase(BaseModel):
    nombre: str
    genero: str
    año: Optional[int] = None
    desarrollador: str
    consolas: List[int] = []
    accesorios: List[int] = []

class JuegoUpdate(JuegoBase):
    id: int

class ConsolaBase(BaseModel):
    nombre: str
    fabricante: str
    año_lanzamiento: Optional[int] = None

class ConsolaUpdate(ConsolaBase):
    id: int

class AccesorioBase(BaseModel):
    nombre: str
    tipo: str
    compatible_con: List[int] = []

class AccesorioUpdate(AccesorioBase):
    id: int

class HistorialBase(BaseModel):
    accion: str
    detalles: str
    tipo_objeto: str
    objeto_id: Optional[int] = None

class ComparacionBase(BaseModel):
    nombre: str
    juego_id: int
    consola_id: int
    accesorio_id: Optional[int] = None
    notas: Optional[str] = None

class ComparacionCreate(ComparacionBase):
    pass

class Comparacion(ComparacionBase):
    id: int
    fecha_creacion: datetime

# --- Lógica de la Base de Datos ---
def get_db():
    """Obtiene una conexión a la base de datos PostgreSQL."""
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    """Inicializa el esquema de la base de datos en PostgreSQL."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS juegos (
        id SERIAL PRIMARY KEY,
        nombre VARCHAR(255) NOT NULL,
        genero VARCHAR(100) NOT NULL,
        año INTEGER,
        desarrollador VARCHAR(255) NOT NULL,
        imagen VARCHAR(255),
        fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS consolas (
        id SERIAL PRIMARY KEY,
        nombre VARCHAR(255) NOT NULL,
        fabricante VARCHAR(255) NOT NULL,
        año_lanzamiento INTEGER,
        imagen VARCHAR(255),
        fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accesorios (
        id SERIAL PRIMARY KEY,
        nombre VARCHAR(255) NOT NULL,
        tipo VARCHAR(100) NOT NULL,
        imagen VARCHAR(255),
        fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS compatibilidad (
        id SERIAL PRIMARY KEY,
        juego_id INTEGER NOT NULL REFERENCES juegos(id) ON DELETE CASCADE,
        consola_id INTEGER NOT NULL REFERENCES consolas(id) ON DELETE CASCADE,
        accesorio_id INTEGER REFERENCES accesorios(id) ON DELETE CASCADE,
        notas TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accesorio_consola (
        id SERIAL PRIMARY KEY,
        accesorio_id INTEGER NOT NULL REFERENCES accesorios(id) ON DELETE CASCADE,
        consola_id INTEGER NOT NULL REFERENCES consolas(id) ON DELETE CASCADE
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historial (
        id SERIAL PRIMARY KEY,
        accion VARCHAR(50) NOT NULL,
        detalles TEXT NOT NULL,
        tipo_objeto VARCHAR(50),
        objeto_id INTEGER,
        fecha TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comparaciones (
        id SERIAL PRIMARY KEY,
        nombre VARCHAR(255) NOT NULL,
        juego_id INTEGER NOT NULL REFERENCES juegos(id) ON DELETE CASCADE,
        consola_id INTEGER NOT NULL REFERENCES consolas(id) ON DELETE CASCADE,
        accesorio_id INTEGER REFERENCES accesorios(id) ON DELETE SET NULL,
        notas TEXT,
        fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()

def registrar_historial(accion: str, detalles: str, tipo_objeto: str = None, objeto_id: int = None):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO historial (accion, detalles, tipo_objeto, objeto_id) VALUES (%s, %s, %s, %s)",
            (accion, detalles, tipo_objeto, objeto_id)
        )
        conn.commit()
    except Exception as e:
        print(f"Error al registrar en historial: {e}")
    finally:
        cursor.close()
        conn.close()

@app.on_event("startup")
async def startup():
    init_db()

# --- Endpoints Completos y Actualizados para PostgreSQL ---

@app.get("/", response_class=HTMLResponse)
async def inicio(request: Request):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("SELECT * FROM juegos ORDER BY id DESC")
        juegos = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM consolas ORDER BY id DESC")
        consolas = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM accesorios ORDER BY id DESC")
        accesorios = [dict(row) for row in cursor.fetchall()]
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "juegos": juegos,
            "consolas": consolas,
            "accesorios": accesorios
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/api/historial", response_class=JSONResponse)
async def obtener_historial(clave: str = Query(...)):
    if clave != "0000":
        raise HTTPException(status_code=403, detail="Clave incorrecta")
    
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("""
            SELECT accion, detalles, tipo_objeto, objeto_id, 
                   to_char(fecha, 'YYYY-MM-DD HH24:MI:SS') as fecha 
            FROM historial 
            ORDER BY fecha DESC 
            LIMIT 50
        """)
        historial = [dict(row) for row in cursor.fetchall()]
        return {"historial": historial}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/api/buscar", response_class=JSONResponse)
async def buscar(
    q: str = Query(..., min_length=1),
    tipo: str = Query("todo", regex="^(juegos|consolas|accesorios|todo)$")
):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        query = f"%{q}%"
        results = {"juegos": [], "consolas": [], "accesorios": []}
        
        if tipo in ["juegos", "todo"]:
            cursor.execute("""
                SELECT * FROM juegos 
                WHERE nombre ILIKE %s OR genero ILIKE %s OR desarrollador ILIKE %s
            """, (query, query, query))
            results["juegos"] = [dict(row) for row in cursor.fetchall()]
        
        if tipo in ["consolas", "todo"]:
            cursor.execute("""
                SELECT * FROM consolas 
                WHERE nombre ILIKE %s OR fabricante ILIKE %s
            """, (query, query))
            results["consolas"] = [dict(row) for row in cursor.fetchall()]
        
        if tipo in ["accesorios", "todo"]:
            cursor.execute("""
                SELECT * FROM accesorios 
                WHERE nombre ILIKE %s OR tipo ILIKE %s
            """, (query, query))
            results["accesorios"] = [dict(row) for row in cursor.fetchall()]
        
        registrar_historial("Búsqueda", f"Búsqueda realizada: '{q}' en {tipo}", None, None)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/juegos", response_class=JSONResponse)
async def crear_juego(
    nombre: str = Form(...),
    genero: str = Form(...),
    año: Optional[int] = Form(None),
    desarrollador: str = Form(...),
    consolas: List[int] = Form([]),
    accesorios: List[int] = Form([]),
    imagen: UploadFile = File(None)
):
    imagen_url = None
    if imagen:
        filename = f"{uuid.uuid4()}.{imagen.filename.split('.')[-1]}"
        filepath = os.path.join(UPLOADS_DIR, filename)
        with open(filepath, "wb") as buffer:
            buffer.write(await imagen.read())
        imagen_url = f"/static/uploads/{filename}"

    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute(
            """
            INSERT INTO juegos (nombre, genero, año, desarrollador, imagen)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
            """,
            (nombre, genero, año, desarrollador, imagen_url)
        )
        juego_id = cursor.fetchone()['id']
        
        for consola_id in consolas:
            cursor.execute(
                "INSERT INTO compatibilidad (juego_id, consola_id) VALUES (%s, %s)",
                (juego_id, consola_id)
            )
        
        for accesorio_id in accesorios:
            cursor.execute("SELECT consola_id FROM accesorio_consola WHERE accesorio_id = %s", (accesorio_id,))
            consolas_accesorio = [row['consola_id'] for row in cursor.fetchall()]
            for consola_id in consolas_accesorio:
                cursor.execute(
                    "INSERT INTO compatibilidad (juego_id, consola_id, accesorio_id) VALUES (%s, %s, %s)",
                    (juego_id, consola_id, accesorio_id)
                )
        
        conn.commit()
        registrar_historial("Creación", f"Juego creado: {nombre}", "juego", juego_id)
        return JSONResponse(status_code=201, content={"message": "Juego creado con éxito", "id": juego_id})
    except Exception as e:
        conn.rollback()
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
    desarrollador: str = Form(...),
    consolas: List[int] = Form([]),
    accesorios: List[int] = Form([]),
    imagen: UploadFile = File(None)
):
    imagen_url = None
    if imagen:
        filename = f"{uuid.uuid4()}.{imagen.filename.split('.')[-1]}"
        filepath = os.path.join(UPLOADS_DIR, filename)
        with open(filepath, "wb") as buffer:
            buffer.write(await imagen.read())
        imagen_url = f"/static/uploads/{filename}"

    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("SELECT nombre FROM juegos WHERE id = %s", (juego_id,))
        fetch = cursor.fetchone()
        if not fetch:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        nombre_actual = fetch['nombre']
        
        if imagen_url:
            cursor.execute(
                """
                UPDATE juegos 
                SET nombre = %s, genero = %s, año = %s, desarrollador = %s, imagen = %s, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (nombre, genero, año, desarrollador, imagen_url, juego_id)
            )
        else:
            cursor.execute(
                """
                UPDATE juegos 
                SET nombre = %s, genero = %s, año = %s, desarrollador = %s, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (nombre, genero, año, desarrollador, juego_id)
            )
        
        cursor.execute("DELETE FROM compatibilidad WHERE juego_id = %s", (juego_id,))
        
        for consola_id in consolas:
            cursor.execute(
                "INSERT INTO compatibilidad (juego_id, consola_id) VALUES (%s, %s)",
                (juego_id, consola_id)
            )
        
        for accesorio_id in accesorios:
            cursor.execute("SELECT consola_id FROM accesorio_consola WHERE accesorio_id = %s", (accesorio_id,))
            consolas_accesorio = [row['consola_id'] for row in cursor.fetchall()]
            for consola_id in consolas_accesorio:
                cursor.execute(
                    "INSERT INTO compatibilidad (juego_id, consola_id, accesorio_id) VALUES (%s, %s, %s)",
                    (juego_id, consola_id, accesorio_id)
                )
        
        conn.commit()
        registrar_historial("Actualización", f"Juego actualizado: {nombre_actual} -> {nombre}", "juego", juego_id)
        return {"message": "Juego actualizado con éxito"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/juegos/{juego_id}", response_class=JSONResponse)
async def eliminar_juego(juego_id: int):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("SELECT nombre FROM juegos WHERE id = %s", (juego_id,))
        fetch = cursor.fetchone()
        if not fetch:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        nombre = fetch['nombre']
        
        cursor.execute("DELETE FROM juegos WHERE id = %s", (juego_id,))
        
        conn.commit()
        registrar_historial("Eliminación", f"Juego eliminado: {nombre}", "juego", juego_id)
        return {"message": "Juego eliminado con éxito"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/consolas", response_class=JSONResponse)
async def crear_consola(
    nombre: str = Form(...),
    fabricante: str = Form(...),
    año_lanzamiento: Optional[int] = Form(None),
    imagen: UploadFile = File(None)
):
    imagen_url = None
    if imagen:
        filename = f"{uuid.uuid4()}.{imagen.filename.split('.')[-1]}"
        filepath = os.path.join(UPLOADS_DIR, filename)
        with open(filepath, "wb") as buffer:
            buffer.write(await imagen.read())
        imagen_url = f"/static/uploads/{filename}"

    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute(
            """
            INSERT INTO consolas (nombre, fabricante, año_lanzamiento, imagen)
            VALUES (%s, %s, %s, %s) RETURNING id
            """,
            (nombre, fabricante, año_lanzamiento, imagen_url)
        )
        consola_id = cursor.fetchone()['id']
        
        conn.commit()
        registrar_historial("Creación", f"Consola creada: {nombre}", "consola", consola_id)
        return JSONResponse(status_code=201, content={"message": "Consola creada con éxito", "id": consola_id})
    except Exception as e:
        conn.rollback()
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
    imagen: UploadFile = File(None)
):
    imagen_url = None
    if imagen:
        filename = f"{uuid.uuid4()}.{imagen.filename.split('.')[-1]}"
        filepath = os.path.join(UPLOADS_DIR, filename)
        with open(filepath, "wb") as buffer:
            buffer.write(await imagen.read())
        imagen_url = f"/static/uploads/{filename}"

    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("SELECT nombre FROM consolas WHERE id = %s", (consola_id,))
        fetch = cursor.fetchone()
        if not fetch:
            raise HTTPException(status_code=404, detail="Consola no encontrada")
        nombre_actual = fetch['nombre']
        
        if imagen_url:
            cursor.execute(
                """
                UPDATE consolas 
                SET nombre = %s, fabricante = %s, año_lanzamiento = %s, imagen = %s, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (nombre, fabricante, año_lanzamiento, imagen_url, consola_id)
            )
        else:
            cursor.execute(
                """
                UPDATE consolas 
                SET nombre = %s, fabricante = %s, año_lanzamiento = %s, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (nombre, fabricante, año_lanzamiento, consola_id)
            )
        
        conn.commit()
        registrar_historial("Actualización", f"Consola actualizada: {nombre_actual} -> {nombre}", "consola", consola_id)
        return {"message": "Consola actualizada con éxito"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/consolas/{consola_id}", response_class=JSONResponse)
async def eliminar_consola(consola_id: int):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("SELECT nombre FROM consolas WHERE id = %s", (consola_id,))
        fetch = cursor.fetchone()
        if not fetch:
            raise HTTPException(status_code=404, detail="Consola no encontrada")
        nombre = fetch['nombre']
        
        cursor.execute("DELETE FROM consolas WHERE id = %s", (consola_id,))
        
        conn.commit()
        registrar_historial("Eliminación", f"Consola eliminada: {nombre}", "consola", consola_id)
        return {"message": "Consola eliminada con éxito"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/accesorios", response_class=JSONResponse)
async def crear_accesorio(
    nombre: str = Form(...),
    tipo: str = Form(...),
    consolas_compatibles: List[int] = Form([]),
    imagen: UploadFile = File(None)
):
    imagen_url = None
    if imagen:
        filename = f"{uuid.uuid4()}.{imagen.filename.split('.')[-1]}"
        filepath = os.path.join(UPLOADS_DIR, filename)
        with open(filepath, "wb") as buffer:
            buffer.write(await imagen.read())
        imagen_url = f"/static/uploads/{filename}"

    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute(
            """
            INSERT INTO accesorios (nombre, tipo, imagen)
            VALUES (%s, %s, %s) RETURNING id
            """,
            (nombre, tipo, imagen_url)
        )
        accesorio_id = cursor.fetchone()['id']
        
        for consola_id in consolas_compatibles:
            cursor.execute(
                "INSERT INTO accesorio_consola (accesorio_id, consola_id) VALUES (%s, %s)",
                (accesorio_id, consola_id)
            )
        
        conn.commit()
        registrar_historial("Creación", f"Accesorio creado: {nombre}", "accesorio", accesorio_id)
        return JSONResponse(status_code=201, content={"message": "Accesorio creado con éxito", "id": accesorio_id})
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.put("/api/accesorios/{accesorio_id}", response_class=JSONResponse)
async def actualizar_accesorio(
    accesorio_id: int,
    nombre: str = Form(...),
    tipo: str = Form(...),
    consolas_compatibles: List[int] = Form([]),
    imagen: UploadFile = File(None)
):
    imagen_url = None
    if imagen:
        filename = f"{uuid.uuid4()}.{imagen.filename.split('.')[-1]}"
        filepath = os.path.join(UPLOADS_DIR, filename)
        with open(filepath, "wb") as buffer:
            buffer.write(await imagen.read())
        imagen_url = f"/static/uploads/{filename}"

    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("SELECT nombre FROM accesorios WHERE id = %s", (accesorio_id,))
        fetch = cursor.fetchone()
        if not fetch:
            raise HTTPException(status_code=404, detail="Accesorio no encontrado")
        nombre_actual = fetch['nombre']
        
        if imagen_url:
            cursor.execute(
                """
                UPDATE accesorios 
                SET nombre = %s, tipo = %s, imagen = %s, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (nombre, tipo, imagen_url, accesorio_id)
            )
        else:
            cursor.execute(
                """
                UPDATE accesorios 
                SET nombre = %s, tipo = %s, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (nombre, tipo, accesorio_id)
            )
        
        cursor.execute("DELETE FROM accesorio_consola WHERE accesorio_id = %s", (accesorio_id,))
        for consola_id in consolas_compatibles:
            cursor.execute(
                "INSERT INTO accesorio_consola (accesorio_id, consola_id) VALUES (%s, %s)",
                (accesorio_id, consola_id)
            )
        
        conn.commit()
        registrar_historial("Actualización", f"Accesorio actualizado: {nombre_actual} -> {nombre}", "accesorio", accesorio_id)
        return {"message": "Accesorio actualizado con éxito"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/accesorios/{accesorio_id}", response_class=JSONResponse)
async def eliminar_accesorio(accesorio_id: int):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("SELECT nombre FROM accesorios WHERE id = %s", (accesorio_id,))
        fetch = cursor.fetchone()
        if not fetch:
            raise HTTPException(status_code=404, detail="Accesorio no encontrado")
        nombre = fetch['nombre']
        
        cursor.execute("DELETE FROM accesorios WHERE id = %s", (accesorio_id,))
        
        conn.commit()
        registrar_historial("Eliminación", f"Accesorio eliminado: {nombre}", "accesorio", accesorio_id)
        return {"message": "Accesorio eliminado con éxito"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/comparaciones", response_class=HTMLResponse)
async def ver_comparaciones(request: Request):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("SELECT * FROM juegos ORDER BY nombre ASC")
        juegos = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM consolas ORDER BY nombre ASC")
        consolas = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM accesorios ORDER BY nombre ASC")
        accesorios = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("""
            SELECT c.*, j.nombre as juego_nombre, con.nombre as consola_nombre, a.nombre as accesorio_nombre
            FROM comparaciones c
            LEFT JOIN juegos j ON c.juego_id = j.id
            LEFT JOIN consolas con ON c.consola_id = con.id
            LEFT JOIN accesorios a ON c.accesorio_id = a.id
            ORDER BY c.fecha_creacion DESC
        """)
        comparaciones = [dict(row) for row in cursor.fetchall()]
        
        return templates.TemplateResponse("comparaciones.html", {
            "request": request,
            "juegos": juegos,
            "consolas": consolas,
            "accesorios": accesorios,
            "comparaciones": comparaciones
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/comparaciones", response_class=JSONResponse)
async def crear_comparacion(
    nombre: str = Form(...),
    juego_id: int = Form(...),
    consola_id: int = Form(...),
    accesorio_id: Optional[int] = Form(None),
    notas: Optional[str] = Form(None)
):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute(
            """
            INSERT INTO comparaciones (nombre, juego_id, consola_id, accesorio_id, notas)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
            """,
            (nombre, juego_id, consola_id, accesorio_id, notas)
        )
        comparacion_id = cursor.fetchone()['id']
        
        cursor.execute("SELECT nombre FROM juegos WHERE id = %s", (juego_id,))
        juego_nombre = cursor.fetchone()['nombre']
        cursor.execute("SELECT nombre FROM consolas WHERE id = %s", (consola_id,))
        consola_nombre = cursor.fetchone()['nombre']
        
        detalles = f"Comparación creada: '{nombre}' ({juego_nombre} con {consola_nombre})"
        if accesorio_id:
            cursor.execute("SELECT nombre FROM accesorios WHERE id = %s", (accesorio_id,))
            accesorio_nombre = cursor.fetchone()['nombre']
            detalles += f" y {accesorio_nombre}"
        
        conn.commit()
        registrar_historial("Comparación", detalles, "comparacion", comparacion_id)
        return JSONResponse(status_code=201, content={"message": "Comparación creada con éxito", "id": comparacion_id})
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)