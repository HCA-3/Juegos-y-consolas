from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import os
import uuid
from datetime import datetime

# Configuración inicial
app = FastAPI(
    title="API Minecraft de Videojuegos",
    description="Sistema completo con búsqueda y gestión de juegos, consolas y accesorios"
)

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "juegos.db")
UPLOADS_DIR = os.path.join(BASE_DIR, "static", "uploads")

# Crear carpetas necesarias
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Configuración de FastAPI
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Modelos Pydantic
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

# Inicializar base de datos
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabla de juegos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS juegos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        genero TEXT NOT NULL,
        año INTEGER,
        desarrollador TEXT NOT NULL,
        imagen TEXT,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Tabla de consolas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS consolas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        fabricante TEXT NOT NULL,
        año_lanzamiento INTEGER,
        imagen TEXT,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Tabla de accesorios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accesorios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        tipo TEXT NOT NULL,
        imagen TEXT,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Tabla de compatibilidad
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS compatibilidad (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        juego_id INTEGER NOT NULL,
        consola_id INTEGER NOT NULL,
        accesorio_id INTEGER,
        notas TEXT,
        FOREIGN KEY(juego_id) REFERENCES juegos(id),
        FOREIGN KEY(consola_id) REFERENCES consolas(id),
        FOREIGN KEY(accesorio_id) REFERENCES accesorios(id)
    )
    """)
    
    # Tabla de compatibilidad accesorios-consolas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accesorio_consola (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        accesorio_id INTEGER NOT NULL,
        consola_id INTEGER NOT NULL,
        FOREIGN KEY(accesorio_id) REFERENCES accesorios(id),
        FOREIGN KEY(consola_id) REFERENCES consolas(id)
    )
    """)
    
    # Tabla de historial
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historial (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        accion TEXT NOT NULL,
        detalles TEXT NOT NULL,
        tipo_objeto TEXT,
        objeto_id INTEGER,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

init_db()

# Funciones de base de datos
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def registrar_historial(accion: str, detalles: str, tipo_objeto: str = None, objeto_id: int = None):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO historial (accion, detalles, tipo_objeto, objeto_id)
            VALUES (?, ?, ?, ?)
            """,
            (accion, detalles, tipo_objeto, objeto_id)
        )
        conn.commit()
    except Exception as e:
        print(f"Error al registrar en historial: {e}")
    finally:
        conn.close()

# Obtener datos completos para la vista
def obtener_datos_completos():
    conn = get_db()
    cursor = conn.cursor()
    
    # Obtener juegos con sus consolas y accesorios
    cursor.execute("SELECT * FROM juegos")
    juegos = cursor.fetchall()
    
    juegos_completos = []
    for juego in juegos:
        # Obtener consolas compatibles
        cursor.execute("""
            SELECT c.id, c.nombre FROM compatibilidad comp
            JOIN consolas c ON comp.consola_id = c.id
            WHERE comp.juego_id = ? AND comp.accesorio_id IS NULL
        """, (juego['id'],))
        consolas = [dict(row) for row in cursor.fetchall()]
        
        # Obtener accesorios compatibles
        cursor.execute("""
            SELECT a.id, a.nombre FROM compatibilidad comp
            JOIN accesorios a ON comp.accesorio_id = a.id
            WHERE comp.juego_id = ?
        """, (juego['id'],))
        accesorios = [dict(row) for row in cursor.fetchall()]
        
        juegos_completos.append({
            **dict(juego),
            'consolas': consolas,
            'accesorios': accesorios
        })
    
    # Obtener todas las consolas
    cursor.execute("SELECT * FROM consolas")
    consolas = [dict(row) for row in cursor.fetchall()]
    
    # Obtener todos los accesorios con sus consolas compatibles
    cursor.execute("SELECT * FROM accesorios")
    accesorios = []
    for accesorio in cursor.fetchall():
        accesorio_dict = dict(accesorio)
        cursor.execute("""
            SELECT c.id, c.nombre FROM accesorio_consola ac
            JOIN consolas c ON ac.consola_id = c.id
            WHERE ac.accesorio_id = ?
        """, (accesorio_dict['id'],))
        accesorio_dict['consolas_compatibles'] = [dict(row) for row in cursor.fetchall()]
        accesorios.append(accesorio_dict)
    
    # Obtener historial
    cursor.execute("SELECT * FROM historial ORDER BY fecha DESC LIMIT 50")
    historial = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "juegos": juegos_completos,
        "consolas": consolas,
        "accesorios": accesorios,
        "historial": historial
    }

# Rutas principales
@app.get("/", response_class=HTMLResponse)
async def inicio(request: Request):
    datos = obtener_datos_completos()
    return templates.TemplateResponse("index.html", {"request": request, **datos})

@app.get("/historial", response_class=HTMLResponse)
async def ver_historial(request: Request, clave: str = Query(None)):
    if clave != "0000":
        raise HTTPException(status_code=403, detail="Clave incorrecta")
    datos = obtener_datos_completos()
    return templates.TemplateResponse("historial.html", {"request": request, "historial": datos["historial"]})

# API para Juegos
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
    # Guardar imagen
    imagen_url = None
    if imagen:
        filename = f"{uuid.uuid4()}.{imagen.filename.split('.')[-1]}"
        filepath = os.path.join(UPLOADS_DIR, filename)
        with open(filepath, "wb") as buffer:
            buffer.write(await imagen.read())
        imagen_url = f"/static/uploads/{filename}"

    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Insertar juego
        cursor.execute(
            """
            INSERT INTO juegos (nombre, genero, año, desarrollador, imagen)
            VALUES (?, ?, ?, ?, ?)
            """,
            (nombre, genero, año, desarrollador, imagen_url)
        )
        juego_id = cursor.lastrowid
        
        # Insertar relaciones con consolas
        for consola_id in consolas:
            cursor.execute(
                """
                INSERT INTO compatibilidad (juego_id, consola_id)
                VALUES (?, ?)
                """,
                (juego_id, consola_id)
            )
        
        # Insertar relaciones con accesorios
        for accesorio_id in accesorios:
            # Obtener consolas compatibles con el accesorio
            cursor.execute("SELECT consola_id FROM accesorio_consola WHERE accesorio_id = ?", (accesorio_id,))
            consolas_accesorio = [row['consola_id'] for row in cursor.fetchall()]
            
            # Crear relación juego-accesorio para cada consola compatible
            for consola_id in consolas_accesorio:
                cursor.execute(
                    """
                    INSERT INTO compatibilidad (juego_id, consola_id, accesorio_id)
                    VALUES (?, ?, ?)
                    """,
                    (juego_id, consola_id, accesorio_id)
                )
        
        conn.commit()
        registrar_historial(
            "Creación",
            f"Juego creado: {nombre}",
            "juego",
            juego_id
        )
        return JSONResponse(
            status_code=201,
            content={"message": "Juego creado con éxito", "id": juego_id}
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
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
    # Guardar imagen si se proporciona
    imagen_url = None
    if imagen:
        filename = f"{uuid.uuid4()}.{imagen.filename.split('.')[-1]}"
        filepath = os.path.join(UPLOADS_DIR, filename)
        with open(filepath, "wb") as buffer:
            buffer.write(await imagen.read())
        imagen_url = f"/static/uploads/{filename}"

    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Obtener nombre actual para el historial
        cursor.execute("SELECT nombre FROM juegos WHERE id = ?", (juego_id,))
        nombre_actual = cursor.fetchone()['nombre']
        
        # Actualizar juego
        if imagen_url:
            cursor.execute(
                """
                UPDATE juegos 
                SET nombre = ?, genero = ?, año = ?, desarrollador = ?, imagen = ?, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (nombre, genero, año, desarrollador, imagen_url, juego_id)
            )
        else:
            cursor.execute(
                """
                UPDATE juegos 
                SET nombre = ?, genero = ?, año = ?, desarrollador = ?, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (nombre, genero, año, desarrollador, juego_id)
            )
        
        # Eliminar relaciones existentes
        cursor.execute("DELETE FROM compatibilidad WHERE juego_id = ?", (juego_id,))
        
        # Insertar nuevas relaciones con consolas
        for consola_id in consolas:
            cursor.execute(
                """
                INSERT INTO compatibilidad (juego_id, consola_id)
                VALUES (?, ?)
                """,
                (juego_id, consola_id)
            )
        
        # Insertar nuevas relaciones con accesorios
        for accesorio_id in accesorios:
            # Obtener consolas compatibles con el accesorio
            cursor.execute("SELECT consola_id FROM accesorio_consola WHERE accesorio_id = ?", (accesorio_id,))
            consolas_accesorio = [row['consola_id'] for row in cursor.fetchall()]
            
            # Crear relación juego-accesorio para cada consola compatible
            for consola_id in consolas_accesorio:
                cursor.execute(
                    """
                    INSERT INTO compatibilidad (juego_id, consola_id, accesorio_id)
                    VALUES (?, ?, ?)
                    """,
                    (juego_id, consola_id, accesorio_id)
                )
        
        conn.commit()
        registrar_historial(
            "Actualización",
            f"Juego actualizado: {nombre_actual} -> {nombre}",
            "juego",
            juego_id
        )
        return {"message": "Juego actualizado con éxito"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.delete("/api/juegos/{juego_id}", response_class=JSONResponse)
async def eliminar_juego(juego_id: int):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Obtener nombre para el historial
        cursor.execute("SELECT nombre FROM juegos WHERE id = ?", (juego_id,))
        nombre = cursor.fetchone()['nombre']
        
        # Eliminar relaciones primero
        cursor.execute("DELETE FROM compatibilidad WHERE juego_id = ?", (juego_id,))
        
        # Eliminar juego
        cursor.execute("DELETE FROM juegos WHERE id = ?", (juego_id,))
        
        conn.commit()
        registrar_historial(
            "Eliminación",
            f"Juego eliminado: {nombre}",
            "juego",
            juego_id
        )
        return {"message": "Juego eliminado con éxito"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

# API para Consolas
@app.post("/api/consolas", response_class=JSONResponse)
async def crear_consola(
    nombre: str = Form(...),
    fabricante: str = Form(...),
    año_lanzamiento: Optional[int] = Form(None),
    imagen: UploadFile = File(None)
):
    # Guardar imagen
    imagen_url = None
    if imagen:
        filename = f"{uuid.uuid4()}.{imagen.filename.split('.')[-1]}"
        filepath = os.path.join(UPLOADS_DIR, filename)
        with open(filepath, "wb") as buffer:
            buffer.write(await imagen.read())
        imagen_url = f"/static/uploads/{filename}"

    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            INSERT INTO consolas (nombre, fabricante, año_lanzamiento, imagen)
            VALUES (?, ?, ?, ?)
            """,
            (nombre, fabricante, año_lanzamiento, imagen_url)
        )
        consola_id = cursor.lastrowid
        
        conn.commit()
        registrar_historial(
            "Creación",
            f"Consola creada: {nombre}",
            "consola",
            consola_id
        )
        return JSONResponse(
            status_code=201,
            content={"message": "Consola creada con éxito", "id": consola_id}
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.put("/api/consolas/{consola_id}", response_class=JSONResponse)
async def actualizar_consola(
    consola_id: int,
    nombre: str = Form(...),
    fabricante: str = Form(...),
    año_lanzamiento: Optional[int] = Form(None),
    imagen: UploadFile = File(None)
):
    # Guardar imagen si se proporciona
    imagen_url = None
    if imagen:
        filename = f"{uuid.uuid4()}.{imagen.filename.split('.')[-1]}"
        filepath = os.path.join(UPLOADS_DIR, filename)
        with open(filepath, "wb") as buffer:
            buffer.write(await imagen.read())
        imagen_url = f"/static/uploads/{filename}"

    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Obtener nombre actual para el historial
        cursor.execute("SELECT nombre FROM consolas WHERE id = ?", (consola_id,))
        nombre_actual = cursor.fetchone()['nombre']
        
        if imagen_url:
            cursor.execute(
                """
                UPDATE consolas 
                SET nombre = ?, fabricante = ?, año_lanzamiento = ?, imagen = ?, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (nombre, fabricante, año_lanzamiento, imagen_url, consola_id)
            )
        else:
            cursor.execute(
                """
                UPDATE consolas 
                SET nombre = ?, fabricante = ?, año_lanzamiento = ?, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (nombre, fabricante, año_lanzamiento, consola_id)
            )
        
        conn.commit()
        registrar_historial(
            "Actualización",
            f"Consola actualizada: {nombre_actual} -> {nombre}",
            "consola",
            consola_id
        )
        return {"message": "Consola actualizada con éxito"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.delete("/api/consolas/{consola_id}", response_class=JSONResponse)
async def eliminar_consola(consola_id: int):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Obtener nombre para el historial
        cursor.execute("SELECT nombre FROM consolas WHERE id = ?", (consola_id,))
        nombre = cursor.fetchone()['nombre']
        
        # Eliminar relaciones primero
        cursor.execute("DELETE FROM compatibilidad WHERE consola_id = ?", (consola_id,))
        cursor.execute("DELETE FROM accesorio_consola WHERE consola_id = ?", (consola_id,))
        
        # Eliminar consola
        cursor.execute("DELETE FROM consolas WHERE id = ?", (consola_id,))
        
        conn.commit()
        registrar_historial(
            "Eliminación",
            f"Consola eliminada: {nombre}",
            "consola",
            consola_id
        )
        return {"message": "Consola eliminada con éxito"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

# API para Accesorios
@app.post("/api/accesorios", response_class=JSONResponse)
async def crear_accesorio(
    nombre: str = Form(...),
    tipo: str = Form(...),
    consolas_compatibles: List[int] = Form([]),
    imagen: UploadFile = File(None)
):
    # Guardar imagen
    imagen_url = None
    if imagen:
        filename = f"{uuid.uuid4()}.{imagen.filename.split('.')[-1]}"
        filepath = os.path.join(UPLOADS_DIR, filename)
        with open(filepath, "wb") as buffer:
            buffer.write(await imagen.read())
        imagen_url = f"/static/uploads/{filename}"

    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Insertar accesorio
        cursor.execute(
            """
            INSERT INTO accesorios (nombre, tipo, imagen)
            VALUES (?, ?, ?)
            """,
            (nombre, tipo, imagen_url)
        )
        accesorio_id = cursor.lastrowid
        
        # Insertar relaciones con consolas
        for consola_id in consolas_compatibles:
            cursor.execute(
                """
                INSERT INTO accesorio_consola (accesorio_id, consola_id)
                VALUES (?, ?)
                """,
                (accesorio_id, consola_id)
            )
        
        conn.commit()
        registrar_historial(
            "Creación",
            f"Accesorio creado: {nombre}",
            "accesorio",
            accesorio_id
        )
        return JSONResponse(
            status_code=201,
            content={"message": "Accesorio creado con éxito", "id": accesorio_id}
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.put("/api/accesorios/{accesorio_id}", response_class=JSONResponse)
async def actualizar_accesorio(
    accesorio_id: int,
    nombre: str = Form(...),
    tipo: str = Form(...),
    consolas_compatibles: List[int] = Form([]),
    imagen: UploadFile = File(None)
):
    # Guardar imagen si se proporciona
    imagen_url = None
    if imagen:
        filename = f"{uuid.uuid4()}.{imagen.filename.split('.')[-1]}"
        filepath = os.path.join(UPLOADS_DIR, filename)
        with open(filepath, "wb") as buffer:
            buffer.write(await imagen.read())
        imagen_url = f"/static/uploads/{filename}"

    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Obtener nombre actual para el historial
        cursor.execute("SELECT nombre FROM accesorios WHERE id = ?", (accesorio_id,))
        nombre_actual = cursor.fetchone()['nombre']
        
        if imagen_url:
            cursor.execute(
                """
                UPDATE accesorios 
                SET nombre = ?, tipo = ?, imagen = ?, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (nombre, tipo, imagen_url, accesorio_id)
            )
        else:
            cursor.execute(
                """
                UPDATE accesorios 
                SET nombre = ?, tipo = ?, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (nombre, tipo, accesorio_id)
            )
        
        # Actualizar relaciones con consolas
        cursor.execute("DELETE FROM accesorio_consola WHERE accesorio_id = ?", (accesorio_id,))
        for consola_id in consolas_compatibles:
            cursor.execute(
                """
                INSERT INTO accesorio_consola (accesorio_id, consola_id)
                VALUES (?, ?)
                """,
                (accesorio_id, consola_id)
            )
        
        conn.commit()
        registrar_historial(
            "Actualización",
            f"Accesorio actualizado: {nombre_actual} -> {nombre}",
            "accesorio",
            accesorio_id
        )
        return {"message": "Accesorio actualizado con éxito"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.delete("/api/accesorios/{accesorio_id}", response_class=JSONResponse)
async def eliminar_accesorio(accesorio_id: int):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Obtener nombre para el historial
        cursor.execute("SELECT nombre FROM accesorios WHERE id = ?", (accesorio_id,))
        nombre = cursor.fetchone()['nombre']
        
        # Eliminar relaciones primero
        cursor.execute("DELETE FROM compatibilidad WHERE accesorio_id = ?", (accesorio_id,))
        cursor.execute("DELETE FROM accesorio_consola WHERE accesorio_id = ?", (accesorio_id,))
        
        # Eliminar accesorio
        cursor.execute("DELETE FROM accesorios WHERE id = ?", (accesorio_id,))
        
        conn.commit()
        registrar_historial(
            "Eliminación",
            f"Accesorio eliminado: {nombre}",
            "accesorio",
            accesorio_id
        )
        return {"message": "Accesorio eliminado con éxito"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

# API para Búsqueda
@app.get("/api/buscar", response_class=JSONResponse)
async def buscar(
    q: str = Query(..., min_length=1),
    tipo: str = Query("todo", regex="^(juegos|consolas|accesorios|todo)$")
):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        query = f"%{q}%"
        results = {"juegos": [], "consolas": [], "accesorios": []}
        
        if tipo in ["juegos", "todo"]:
            cursor.execute("""
                SELECT * FROM juegos 
                WHERE nombre LIKE ? OR genero LIKE ? OR desarrollador LIKE ?
            """, (query, query, query))
            results["juegos"] = [dict(row) for row in cursor.fetchall()]
        
        if tipo in ["consolas", "todo"]:
            cursor.execute("""
                SELECT * FROM consolas 
                WHERE nombre LIKE ? OR fabricante LIKE ?
            """, (query, query))
            results["consolas"] = [dict(row) for row in cursor.fetchall()]
        
        if tipo in ["accesorios", "todo"]:
            cursor.execute("""
                SELECT * FROM accesorios 
                WHERE nombre LIKE ? OR tipo LIKE ?
            """, (query, query))
            results["accesorios"] = [dict(row) for row in cursor.fetchall()]
        
        registrar_historial(
            "Búsqueda",
            f"Búsqueda realizada: '{q}' en {tipo}",
            None,
            None
        )
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# API para Historial
@app.get("/api/historial", response_class=JSONResponse)
async def obtener_historial(clave: str = Query(...)):
    if clave != "0000":
        raise HTTPException(status_code=403, detail="Clave incorrecta")
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM historial ORDER BY fecha DESC LIMIT 50")
        historial = [dict(row) for row in cursor.fetchall()]
        return {"historial": historial}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)