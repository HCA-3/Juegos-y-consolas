from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
from typing import List, Optional, Type, TypeVar
import csv
import os
import uvicorn

# Definición de modelos
class ModeloBase:
    def __init__(self, id: str):
        self.id = id
        self.fecha_creacion = datetime.now().isoformat()
        self.activo = True
    
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

class Juego(ModeloBase):
    def __init__(self, id: str, titulo: str, genero: str, desarrollador: str, 
                 año: int, consolas: List[str], precio: float):
        super().__init__(id)
        self.titulo = titulo
        self.genero = genero
        self.desarrollador = desarrollador
        self.año_lanzamiento = año
        self.consolas_compatibles = consolas
        self.precio = precio

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data['id'],
            titulo=data['titulo'],
            genero=data['genero'],
            desarrollador=data['desarrollador'],
            año=int(data['año_lanzamiento']),
            consolas=data['consolas_compatibles'].split(','),
            precio=float(data['precio'])
        )

class Consola(ModeloBase):
    def __init__(self, id: str, nombre: str, fabricante: str, año: int, 
                 generacion: int, precio: float, juegos: List[str]):
        super().__init__(id)
        self.nombre = nombre
        self.fabricante = fabricante
        self.año_lanzamiento = año
        self.generacion = generacion
        self.precio = precio
        self.juegos_compatibles = juegos

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data['id'],
            nombre=data['nombre'],
            fabricante=data['fabricante'],
            año=int(data['año_lanzamiento']),
            generacion=int(data['generacion']),
            precio=float(data['precio']),
            juegos=data['juegos_compatibles'].split(',')
        )

class Accesorio(ModeloBase):
    def __init__(self, id: str, nombre: str, tipo: str, compatible_con: List[str], 
                 precio: float, descripcion: str):
        super().__init__(id)
        self.nombre = nombre
        self.tipo = tipo
        self.compatible_con = compatible_con
        self.precio = precio
        self.descripcion = descripcion

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data['id'],
            nombre=data['nombre'],
            tipo=data['tipo'],
            compatible_con=data['compatible_con'].split(','),
            precio=float(data['precio']),
            descripcion=data['descripcion']
        )

class Historial:
    def __init__(self, accion: str, modelo: str, objeto_id: str, detalles: str):
        self.fecha = datetime.now().isoformat()
        self.accion = accion
        self.modelo = modelo
        self.objeto_id = objeto_id
        self.detalles = detalles
    
    def to_dict(self):
        return self.__dict__

# Operaciones CRUD
T = TypeVar('T', Juego, Consola, Accesorio)

class CRUDBase:
    @staticmethod
    def _guardar_csv(archivo: str, datos: list):
        os.makedirs('data', exist_ok=True)
        if not datos:
            return
        
        with open(f'data/{archivo}', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=datos[0].keys())
            writer.writeheader()
            writer.writerows(datos)
    
    @staticmethod
    def _leer_csv(archivo: str) -> list:
        if not os.path.exists(f'data/{archivo}'):
            return []
        
        with open(f'data/{archivo}', 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))

    @classmethod
    def crear(cls, objeto: T, archivo: str) -> T:
        objetos = cls._leer_csv(archivo)
        objetos.append(objeto.to_dict())
        cls._guardar_csv(archivo, objetos)
        return objeto
    
    @classmethod
    def obtener_todos(cls, archivo: str, clase: Type[T]) -> List[T]:
        datos = cls._leer_csv(archivo)
        return [clase.from_dict(item) for item in datos if item.get('activo', 'True') == 'True']
    
    @classmethod
    def obtener_por_id(cls, id: str, archivo: str, clase: Type[T]) -> Optional[T]:
        datos = cls._leer_csv(archivo)
        for item in datos:
            if item['id'] == id and item.get('activo', 'True') == 'True':
                return clase.from_dict(item)
        return None
    
    @classmethod
    def actualizar(cls, id: str, nuevos_datos: dict, archivo: str, clase: Type[T]) -> Optional[T]:
        objetos = cls._leer_csv(archivo)
        encontrado = False
        
        for obj in objetos:
            if obj['id'] == id:
                obj.update({k: str(v) for k, v in nuevos_datos.items() if k in obj})
                encontrado = True
                break
        
        if encontrado:
            cls._guardar_csv(archivo, objetos)
            return cls.obtener_por_id(id, archivo, clase)
        return None
    
    @classmethod
    def eliminar(cls, id: str, archivo: str) -> bool:
        objetos = cls._leer_csv(archivo)
        encontrado = False
        
        for obj in objetos:
            if obj['id'] == id:
                obj['activo'] = 'False'
                encontrado = True
                break
        
        if encontrado:
            cls._guardar_csv(archivo, objetos)
            return True
        return False

class JuegoCRUD(CRUDBase):
    @classmethod
    def buscar_por_genero(cls, genero: str) -> List[Juego]:
        juegos = cls.obtener_todos('juegos.csv', Juego)
        return [j for j in juegos if j.genero.lower() == genero.lower()]
    
    @classmethod
    def buscar_por_fecha(cls, fecha_inicio: str, fecha_fin: str) -> List[Juego]:
        juegos = cls.obtener_todos('juegos.csv', Juego)
        return [j for j in juegos if fecha_inicio <= j.fecha_creacion <= fecha_fin]

class ConsolaCRUD(CRUDBase):
    @classmethod
    def buscar_por_fabricante(cls, fabricante: str) -> List[Consola]:
        consolas = cls.obtener_todos('consolas.csv', Consola)
        return [c for c in consolas if c.fabricante.lower() == fabricante.lower()]
    
    @classmethod
    def buscar_por_generacion(cls, generacion: int) -> List[Consola]:
        consolas = cls.obtener_todos('consolas.csv', Consola)
        return [c for c in consolas if c.generacion == generacion]

class AccesorioCRUD(CRUDBase):
    @classmethod
    def buscar_por_tipo(cls, tipo: str) -> List[Accesorio]:
        accesorios = cls.obtener_todos('accesorios.csv', Accesorio)
        return [a for a in accesorios if a.tipo.lower() == tipo.lower()]
    
    @classmethod
    def buscar_por_compatibilidad(cls, modelo: str) -> List[Accesorio]:
        accesorios = cls.obtener_todos('accesorios.csv', Accesorio)
        return [a for a in accesorios if modelo.lower() in [c.lower() for c in a.compatible_con]]

class HistorialCRUD(CRUDBase):
    @classmethod
    def registrar(cls, accion: str, modelo: str, objeto_id: str, detalles: str):
        historial = Historial(accion, modelo, objeto_id, detalles)
        historiales = cls._leer_csv('historial.csv')
        historiales.append(historial.to_dict())
        cls._guardar_csv('historial.csv', historiales)
    
    @classmethod
    def obtener_historial(cls) -> List[Historial]:
        datos = cls._leer_csv('historial.csv')
        return [Historial(**item) for item in datos]

# Configuración de FastAPI
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Endpoints para Juegos
@app.post("/juegos/", response_model=Juego)
async def crear_juego(juego: Juego):
    nuevo_juego = JuegoCRUD.crear(juego, 'juegos.csv')
    HistorialCRUD.registrar("CREATE", "Juego", juego.id, f"Juego {juego.titulo} creado")
    return nuevo_juego

@app.get("/juegos/", response_model=List[Juego])
async def listar_juegos():
    return JuegoCRUD.obtener_todos('juegos.csv', Juego)

@app.get("/juegos/{juego_id}", response_model=Juego)
async def obtener_juego(juego_id: str):
    juego = JuegoCRUD.obtener_por_id(juego_id, 'juegos.csv', Juego)
    if not juego:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    return juego

@app.put("/juegos/{juego_id}", response_model=Juego)
async def actualizar_juego(juego_id: str, juego: Juego):
    actualizado = JuegoCRUD.actualizar(juego_id, juego.to_dict(), 'juegos.csv', Juego)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    HistorialCRUD.registrar("UPDATE", "Juego", juego_id, "Datos actualizados")
    return actualizado

@app.delete("/juegos/{juego_id}")
async def eliminar_juego(juego_id: str):
    if not JuegoCRUD.eliminar(juego_id, 'juegos.csv'):
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    HistorialCRUD.registrar("DELETE", "Juego", juego_id, "Juego marcado como inactivo")
    return {"message": "Juego eliminado correctamente"}

@app.get("/juegos/genero/{genero}", response_model=List[Juego])
async def buscar_juegos_por_genero(genero: str):
    return JuegoCRUD.buscar_por_genero(genero)

@app.get("/juegos/fecha/{fecha_inicio}/{fecha_fin}", response_model=List[Juego])
async def buscar_juegos_por_fecha(fecha_inicio: str, fecha_fin: str):
    return JuegoCRUD.buscar_por_fecha(fecha_inicio, fecha_fin)

# Endpoints para Consolas
@app.post("/consolas/", response_model=Consola)
async def crear_consola(consola: Consola):
    nueva_consola = ConsolaCRUD.crear(consola, 'consolas.csv')
    HistorialCRUD.registrar("CREATE", "Consola", consola.id, f"Consola {consola.nombre} creada")
    return nueva_consola

@app.get("/consolas/", response_model=List[Consola])
async def listar_consolas():
    return ConsolaCRUD.obtener_todos('consolas.csv', Consola)

@app.get("/consolas/{consola_id}", response_model=Consola)
async def obtener_consola(consola_id: str):
    consola = ConsolaCRUD.obtener_por_id(consola_id, 'consolas.csv', Consola)
    if not consola:
        raise HTTPException(status_code=404, detail="Consola no encontrada")
    return consola

@app.put("/consolas/{consola_id}", response_model=Consola)
async def actualizar_consola(consola_id: str, consola: Consola):
    actualizada = ConsolaCRUD.actualizar(consola_id, consola.to_dict(), 'consolas.csv', Consola)
    if not actualizada:
        raise HTTPException(status_code=404, detail="Consola no encontrada")
    HistorialCRUD.registrar("UPDATE", "Consola", consola_id, "Datos actualizados")
    return actualizada

@app.delete("/consolas/{consola_id}")
async def eliminar_consola(consola_id: str):
    if not ConsolaCRUD.eliminar(consola_id, 'consolas.csv'):
        raise HTTPException(status_code=404, detail="Consola no encontrada")
    HistorialCRUD.registrar("DELETE", "Consola", consola_id, "Consola marcada como inactiva")
    return {"message": "Consola eliminada correctamente"}

# Endpoints para Accesorios
@app.post("/accesorios/", response_model=Accesorio)
async def crear_accesorio(accesorio: Accesorio):
    nuevo_accesorio = AccesorioCRUD.crear(accesorio, 'accesorios.csv')
    HistorialCRUD.registrar("CREATE", "Accesorio", accesorio.id, f"Accesorio {accesorio.nombre} creado")
    return nuevo_accesorio

@app.get("/accesorios/", response_model=List[Accesorio])
async def listar_accesorios():
    return AccesorioCRUD.obtener_todos('accesorios.csv', Accesorio)

@app.get("/accesorios/{accesorio_id}", response_model=Accesorio)
async def obtener_accesorio(accesorio_id: str):
    accesorio = AccesorioCRUD.obtener_por_id(accesorio_id, 'accesorios.csv', Accesorio)
    if not accesorio:
        raise HTTPException(status_code=404, detail="Accesorio no encontrado")
    return accesorio

# Endpoint para el historial
@app.get("/historial/")
async def obtener_historial():
    return HistorialCRUD.obtener_historial()

# Endpoint para la página principal
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)