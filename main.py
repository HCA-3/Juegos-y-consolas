from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form
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
    description="Sistema completo de gestión de juegos, consolas y accesorios con estilo Minecraft"
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

class ConsolaBase(BaseModel):
    nombre: str
    fabricante: str
    año_lanzamiento: Optional[int] = None

class AccesorioBase(BaseModel):
    nombre: str
    tipo: str
    compatible_con: str  # IDs de consolas separados por comas

class CompatibilidadBase(BaseModel):
    juego_id: int
    consola_id: int
    accesorio_id: Optional[int] = None
    notas: Optional[str] = None

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
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Tabla de accesorios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accesorios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        tipo TEXT NOT NULL,
        compatible_con TEXT,
        imagen TEXT,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    conn.commit()
    conn.close()

init_db()

# Funciones de base de datos
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Obtener datos completos para la vista
def obtener_datos_completos():
    conn = get_db()
    cursor = conn.cursor()
    
    # Obtener juegos con sus consolas compatibles
    cursor.execute("SELECT * FROM juegos")
    juegos = cursor.fetchall()
    
    juegos_completos = []
    for juego in juegos:
        cursor.execute("""
        SELECT c.* FROM compatibilidad comp
        JOIN consolas c ON comp.consola_id = c.id
        WHERE comp.juego_id = ? AND comp.accesorio_id IS NULL
        """, (juego['id'],))
        consolas = cursor.fetchall()
        
        juegos_completos.append({
            **dict(juego),
            'consolas': consolas
        })
    
    # Obtener todas las consolas
    cursor.execute("SELECT * FROM consolas")
    consolas = cursor.fetchall()
    
    # Obtener todos los accesorios
    cursor.execute("SELECT * FROM accesorios")
    accesorios = cursor.fetchall()
    
    # Obtener relaciones de compatibilidad
    cursor.execute("""
    SELECT comp.id, j.nombre as juego, c.nombre as consola, 
           a.nombre as accesorio, comp.notas
    FROM compatibilidad comp
    LEFT JOIN juegos j ON comp.juego_id = j.id
    LEFT JOIN consolas c ON comp.consola_id = c.id
    LEFT JOIN accesorios a ON comp.accesorio_id = a.id
    """)
    compatibilidades = cursor.fetchall()
    
    conn.close()
    
    return {
        "juegos": juegos_completos,
        "consolas": consolas,
        "accesorios": accesorios,
        "compatibilidades": compatibilidades
    }

# Rutas principales
@app.get("/", response_class=HTMLResponse)
async def inicio(request: Request):
    datos = obtener_datos_completos()
    return templates.TemplateResponse("index.html", {"request": request, **datos})

# API para Juegos
@app.post("/api/juegos", response_class=JSONResponse)
async def crear_juego(
    nombre: str = Form(...),
    genero: str = Form(...),
    año: Optional[int] = Form(None),
    desarrollador: str = Form(...),
    imagen: UploadFile = File(None),
    consolas: List[int] = Form([])
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
        
        conn.commit()
        return JSONResponse(
            status_code=201,
            content={"message": "Juego creado con éxito", "id": juego_id}
        )
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
        # Eliminar relaciones primero
        cursor.execute("DELETE FROM compatibilidad WHERE juego_id = ?", (juego_id,))
        
        # Eliminar juego
        cursor.execute("DELETE FROM juegos WHERE id = ?", (juego_id,))
        
        conn.commit()
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
        conn.commit()
        return JSONResponse(
            status_code=201,
            content={"message": "Consola creada con éxito"}
        )
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
    compatible_con: str = Form(...),
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
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            INSERT INTO accesorios (nombre, tipo, compatible_con, imagen)
            VALUES (?, ?, ?, ?)
            """,
            (nombre, tipo, compatible_con, imagen_url)
        )
        conn.commit()
        return JSONResponse(
            status_code=201,
            content={"message": "Accesorio creado con éxito"}
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

# API para Compatibilidad
@app.post("/api/compatibilidad", response_class=JSONResponse)
async def crear_compatibilidad(
    juego_id: int = Form(...),
    consola_id: int = Form(...),
    accesorio_id: Optional[int] = Form(None),
    notas: Optional[str] = Form(None)
):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            INSERT INTO compatibilidad (juego_id, consola_id, accesorio_id, notas)
            VALUES (?, ?, ?, ?)
            """,
            (juego_id, consola_id, accesorio_id, notas)
        )
        conn.commit()
        return JSONResponse(
            status_code=201,
            content={"message": "Compatibilidad establecida con éxito"}
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)