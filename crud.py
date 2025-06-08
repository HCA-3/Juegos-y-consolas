from modelos import *
import csv
import os
from typing import List, Optional, Type, TypeVar

T = TypeVar('T', Juego, Consola, Accesorio)

class CRUDBase:
    @staticmethod
    def _guardar_csv(archivo: str, datos: list):
        """Guarda una lista de diccionarios en CSV"""
        os.makedirs('data', exist_ok=True)
        if not datos:
            return
        
        with open(f'data/{archivo}', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=datos[0].keys())
            writer.writeheader()
            writer.writerows(datos)
    
    @staticmethod
    def _leer_csv(archivo: str) -> list:
        """Lee un archivo CSV y retorna una lista de diccionarios"""
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
                obj.update({k: v for k, v in nuevos_datos.items() if k in obj})
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