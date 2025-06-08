from datetime import datetime
from typing import List, Optional
import csv
import os

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
        self.accion = accion  # CREATE, READ, UPDATE, DELETE
        self.modelo = modelo  # Juego, Consola, Accesorio
        self.objeto_id = objeto_id
        self.detalles = detalles
    
    def to_dict(self):
        return self.__dict__