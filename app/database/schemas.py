from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TipoAccesorio(str, Enum):
    mando = "mando"
    audifonos = "audifonos"
    carga = "carga"
    vr = "realidad_virtual"
    otro = "otro"

class GeneroJuego(str, Enum):
    accion = "acción"
    aventura = "aventura"
    deportes = "deportes"
    estrategia = "estrategia"
    rpg = "RPG"
    shooter = "shooter"
    simulacion = "simulación"
    lucha = "lucha"
    plataformas = "plataformas"

class ConsolaBase(BaseModel):
    nombre: str = Field(..., max_length=100, example="PlayStation 5")
    fabricante: str = Field(..., max_length=100, example="Sony")
    año_lanzamiento: int = Field(..., gt=1970, example=2020)
    generacion: int = Field(..., gt=0, example=9)
    precio: Optional[float] = Field(None, gt=0, example=499.99)
    especificaciones: Optional[str] = Field(None, example="CPU: 3.5GHz, GPU: 10.3 TFLOPS")

class ConsolaCreate(ConsolaBase):
    pass

class ConsolaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    fabricante: Optional[str] = Field(None, max_length=100)
    año_lanzamiento: Optional[int] = Field(None, gt=1970)
    generacion: Optional[int] = Field(None, gt=0)
    precio: Optional[float] = Field(None, gt=0)
    especificaciones: Optional[str] = None

class Consola(ConsolaBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    activo: bool
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "nombre": "PlayStation 5",
                "fabricante": "Sony",
                "año_lanzamiento": 2020,
                "generacion": 9,
                "precio": 499.99,
                "especificaciones": "CPU: 3.5GHz, GPU: 10.3 TFLOPS",
                "fecha_creacion": "2023-01-01T00:00:00",
                "fecha_actualizacion": "2023-01-01T00:00:00",
                "activo": True
            }
        }

class JuegoBase(BaseModel):
    titulo: str = Field(..., max_length=100, example="The Legend of Zelda: Breath of the Wild")
    desarrollador: str = Field(..., max_length=100, example="Nintendo EPD")
    genero: GeneroJuego = Field(..., example="aventura")
    año_lanzamiento: int = Field(..., gt=1970, example=2017)
    precio: float = Field(..., gt=0, example=59.99)
    descripcion: Optional[str] = Field(None, example="Un juego de aventuras en mundo abierto")
    consola_id: int = Field(..., gt=0, example=1)

class JuegoCreate(JuegoBase):
    pass

class JuegoUpdate(BaseModel):
    titulo: Optional[str] = Field(None, max_length=100)
    desarrollador: Optional[str] = Field(None, max_length=100)
    genero: Optional[GeneroJuego] = None
    año_lanzamiento: Optional[int] = Field(None, gt=1970)
    precio: Optional[float] = Field(None, gt=0)
    descripcion: Optional[str] = None
    consola_id: Optional[int] = Field(None, gt=0)

class Juego(JuegoBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    activo: bool
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "titulo": "The Legend of Zelda: Breath of the Wild",
                "desarrollador": "Nintendo EPD",
                "genero": "aventura",
                "año_lanzamiento": 2017,
                "precio": 59.99,
                "descripcion": "Un juego de aventuras en mundo abierto",
                "consola_id": 1,
                "fecha_creacion": "2023-01-01T00:00:00",
                "fecha_actualizacion": "2023-01-01T00:00:00",
                "activo": True
            }
        }

class AccesorioBase(BaseModel):
    nombre: str = Field(..., max_length=100, example="DualSense")
    tipo: TipoAccesorio = Field(..., example="mando")
    descripcion: Optional[str] = Field(None, example="Control inalámbrico con retroalimentación háptica")
    precio: float = Field(..., gt=0, example=69.99)
    consola_id: int = Field(..., gt=0, example=1)

class AccesorioCreate(AccesorioBase):
    pass

class AccesorioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    tipo: Optional[TipoAccesorio] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = Field(None, gt=0)
    consola_id: Optional[int] = Field(None, gt=0)

class Accesorio(AccesorioBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    activo: bool
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "nombre": "DualSense",
                "tipo": "mando",
                "descripcion": "Control inalámbrico con retroalimentación háptica",
                "precio": 69.99,
                "consola_id": 1,
                "fecha_creacion": "2023-01-01T00:00:00",
                "fecha_actualizacion": "2023-01-01T00:00:00",
                "activo": True
            }
        }

class HistorialBase(BaseModel):
    tipo_entidad: str = Field(..., example="juego")
    entidad_id: int = Field(..., gt=0, example=1)
    accion: str = Field(..., example="creacion")
    datos: str = Field(..., example="{'titulo': 'Juego Demo'}")
    usuario: Optional[str] = Field(None, example="admin")

class HistorialCreate(HistorialBase):
    pass

class Historial(HistorialBase):
    id: int
    fecha_accion: datetime
    juego_id: Optional[int] = None
    consola_id: Optional[int] = None
    accesorio_id: Optional[int] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "tipo_entidad": "juego",
                "entidad_id": 1,
                "accion": "creacion",
                "datos": "{'titulo': 'Juego Demo'}",
                "usuario": "admin",
                "fecha_accion": "2023-01-01T00:00:00",
                "juego_id": 1
            }
        }

class CatalogoBase(BaseModel):
    nombre: str = Field(..., max_length=100, example="Los más vendidos 2023")
    descripcion: Optional[str] = Field(None, example="Juegos más vendidos este año")

class CatalogoCreate(CatalogoBase):
    juego_ids: List[int] = Field([], example=[1, 2, 3])

class Catalogo(CatalogoBase):
    id: int
    fecha_creacion: datetime
    activo: bool
    
    class Config:
        from_attributes = True

class ComparacionBase(BaseModel):
    titulo: str = Field(..., max_length=100, example="PS5 vs Xbox Series X")
    descripcion: Optional[str] = Field(None, example="Comparativa de características")

class ComparacionCreate(ComparacionBase):
    consola_ids: List[int] = Field([], example=[1, 2])
    juego_ids: List[int] = Field([], example=[1, 2, 3])
    accesorio_ids: List[int] = Field([], example=[1, 2])

class Comparacion(ComparacionBase):
    id: int
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True

class ImageResponse(BaseModel):
    id: int
    tipo: str
    url: HttpUrl
    
    class Config:
        from_attributes = True