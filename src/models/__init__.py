"""
Inicialización de modelos del sistema de videojuegos
"""
from src.models.database import db, BaseModel
from src.models.juegos import Juego
from src.models.consolas import Consola
from src.models.accesorios import Accesorio
from src.models.historial import HistorialAccion

__all__ = ['db', 'BaseModel', 'Juego', 'Consola', 'Accesorio', 'HistorialAccion']

