"""
Servicio para el catálogo general del sistema
"""
from typing import Dict, List
from src.models import db, Juego, Consola, Accesorio
from src.services.juegos_service import JuegosService
from src.services.consolas_service import ConsolasService
from src.services.accesorios_service import AccesoriosService

class CatalogoService:
    """Servicio para consultas del catálogo general"""
    
    def __init__(self):
        self.juegos_service = JuegosService()
        self.consolas_service = ConsolasService()
        self.accesorios_service = AccesoriosService()
    
    def buscar_global(self, termino: str, page: int = 1, per_page: int = 20) -> Dict:
        """Búsqueda global en todos los tipos de productos"""
        try:
            # Buscar en juegos
            juegos_result = self.juegos_service.buscar_global(termino, page, per_page)
            
            # Buscar en consolas
            consolas_result = self.consolas_service.buscar_global(termino, page, per_page)
            
            # Buscar en accesorios
            accesorios_result = self.accesorios_service.buscar_global(termino, page, per_page)
            
            return {
                'termino_busqueda': termino,
                'juegos': {
                    'total': juegos_result['total'],
                    'items': juegos_result['items'][:5]  # Limitar a 5 resultados
                },
                'consolas': {
                    'total': consolas_result['total'],
                    'items': consolas_result['items'][:5]
                },
                'accesorios': {
                    'total': accesorios_result['total'],
                    'items': accesorios_result['items'][:5]
                },
                'total_general': juegos_result['total'] + consolas_result['total'] + accesorios_result['total']
            }
            
        except Exception as e:
            print(f"Error en búsqueda global del catálogo: {e}")
            return {
                'termino_busqueda': termino,
                'juegos': {'total': 0, 'items': []},
                'consolas': {'total': 0, 'items': []},
                'accesorios': {'total': 0, 'items': []},
                'total_general': 0
            }
    
    def obtener_destacados(self) -> Dict:
        """Obtiene productos destacados de cada categoría"""
        try:
            # Juegos mejor calificados
            juegos_destacados = self.juegos_service.obtener_mejor_calificados(5)
            
            # Consolas más recientes
            consolas_destacadas = self.consolas_service.obtener_mas_recientes(5)
            
            # Accesorios más recientes
            accesorios_destacados = self.accesorios_service.obtener_mas_recientes(5)
            
            return {
                'juegos_destacados': juegos_destacados,
                'consolas_destacadas': consolas_destacadas,
                'accesorios_destacados': accesorios_destacados
            }
            
        except Exception as e:
            print(f"Error obteniendo productos destacados: {e}")
            return {
                'juegos_destacados': [],
                'consolas_destacadas': [],
                'accesorios_destacados': []
            }
    
    def obtener_estadisticas_generales(self) -> Dict:
        """Obtiene estadísticas generales del catálogo"""
        try:
            # Estadísticas de cada categoría
            stats_juegos = self.juegos_service.obtener_estadisticas()
            stats_consolas = self.consolas_service.obtener_estadisticas()
            stats_accesorios = self.accesorios_service.obtener_estadisticas()
            
            return {
                'resumen': {
                    'total_juegos': stats_juegos['total_juegos'],
                    'total_consolas': stats_consolas['total_consolas'],
                    'total_accesorios': stats_accesorios['total_accesorios'],
                    'total_productos': (
                        stats_juegos['total_juegos'] + 
                        stats_consolas['total_consolas'] + 
                        stats_accesorios['total_accesorios']
                    )
                },
                'precios': {
                    'precio_promedio_juegos': stats_juegos['precio_promedio'],
                    'precio_promedio_consolas': stats_consolas['precio_promedio'],
                    'precio_promedio_accesorios': stats_accesorios['precio_promedio']
                },
                'juegos': stats_juegos,
                'consolas': stats_consolas,
                'accesorios': stats_accesorios
            }
            
        except Exception as e:
            print(f"Error obteniendo estadísticas generales: {e}")
            return {
                'resumen': {
                    'total_juegos': 0,
                    'total_consolas': 0,
                    'total_accesorios': 0,
                    'total_productos': 0
                },
                'precios': {
                    'precio_promedio_juegos': 0,
                    'precio_promedio_consolas': 0,
                    'precio_promedio_accesorios': 0
                },
                'juegos': {},
                'consolas': {},
                'accesorios': {}
            }
    
    def obtener_por_categoria(self, categoria: str, page: int = 1, per_page: int = 20) -> Dict:
        """Obtiene productos por categoría específica"""
        try:
            if categoria.lower() == 'juegos':
                return self.juegos_service.obtener_todos(page, per_page)
            elif categoria.lower() == 'consolas':
                return self.consolas_service.obtener_todos(page, per_page)
            elif categoria.lower() == 'accesorios':
                return self.accesorios_service.obtener_todos(page, per_page)
            else:
                return {
                    'items': [],
                    'total': 0,
                    'pages': 0,
                    'current_page': page,
                    'per_page': per_page,
                    'has_next': False,
                    'has_prev': False,
                    'error': f'Categoría "{categoria}" no válida'
                }
                
        except Exception as e:
            print(f"Error obteniendo productos por categoría {categoria}: {e}")
            return {
                'items': [],
                'total': 0,
                'pages': 0,
                'current_page': page,
                'per_page': per_page,
                'has_next': False,
                'has_prev': False,
                'error': str(e)
            }
    
    def obtener_filtros_disponibles(self) -> Dict:
        """Obtiene todos los filtros disponibles para el catálogo"""
        try:
            from sqlalchemy import func
            
            # Géneros de juegos
            generos = db.session.query(Juego.genero).filter(
                Juego.activo == True,
                Juego.genero.isnot(None)
            ).distinct().all()
            
            # Plataformas de juegos
            plataformas = db.session.query(Juego.plataforma).filter(
                Juego.activo == True,
                Juego.plataforma.isnot(None)
            ).distinct().all()
            
            # Fabricantes de consolas
            fabricantes_consolas = db.session.query(Consola.fabricante).filter(
                Consola.activo == True,
                Consola.fabricante.isnot(None)
            ).distinct().all()
            
            # Tipos de consolas
            tipos_consolas = db.session.query(Consola.tipo).filter(
                Consola.activo == True,
                Consola.tipo.isnot(None)
            ).distinct().all()
            
            # Tipos de accesorios
            tipos_accesorios = db.session.query(Accesorio.tipo).filter(
                Accesorio.activo == True,
                Accesorio.tipo.isnot(None)
            ).distinct().all()
            
            # Fabricantes de accesorios
            fabricantes_accesorios = db.session.query(Accesorio.fabricante).filter(
                Accesorio.activo == True,
                Accesorio.fabricante.isnot(None)
            ).distinct().all()
            
            return {
                'juegos': {
                    'generos': [g[0] for g in generos if g[0]],
                    'plataformas': [p[0] for p in plataformas if p[0]]
                },
                'consolas': {
                    'fabricantes': [f[0] for f in fabricantes_consolas if f[0]],
                    'tipos': [t[0] for t in tipos_consolas if t[0]]
                },
                'accesorios': {
                    'tipos': [t[0] for t in tipos_accesorios if t[0]],
                    'fabricantes': [f[0] for f in fabricantes_accesorios if f[0]]
                }
            }
            
        except Exception as e:
            print(f"Error obteniendo filtros disponibles: {e}")
            return {
                'juegos': {'generos': [], 'plataformas': []},
                'consolas': {'fabricantes': [], 'tipos': []},
                'accesorios': {'tipos': [], 'fabricantes': []}
            }

