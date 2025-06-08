"""
Servicio específico para el modelo Juegos
"""
from typing import Dict, List
from sqlalchemy import or_, and_
from src.services.crud_service import CRUDService
from src.models.juegos import Juego
from src.models import db

class JuegosService(CRUDService):
    """Servicio específico para gestión de juegos"""
    
    def __init__(self):
        super().__init__(Juego)
    
    def _aplicar_filtros_busqueda(self, query, criterios: Dict):
        """Aplica filtros de búsqueda específicos para juegos"""
        
        # Búsqueda por nombre
        if criterios.get('nombre'):
            query = query.filter(
                Juego.nombre.ilike(f"%{criterios['nombre']}%")
            )
        
        # Filtro por género
        if criterios.get('genero'):
            query = query.filter(
                Juego.genero.ilike(f"%{criterios['genero']}%")
            )
        
        # Filtro por plataforma
        if criterios.get('plataforma'):
            query = query.filter(
                Juego.plataforma.ilike(f"%{criterios['plataforma']}%")
            )
        
        # Filtro por desarrollador
        if criterios.get('desarrollador'):
            query = query.filter(
                Juego.desarrollador.ilike(f"%{criterios['desarrollador']}%")
            )
        
        # Filtro por editor
        if criterios.get('editor'):
            query = query.filter(
                Juego.editor.ilike(f"%{criterios['editor']}%")
            )
        
        # Filtro por rango de precio
        if criterios.get('precio_min'):
            query = query.filter(Juego.precio >= criterios['precio_min'])
        
        if criterios.get('precio_max'):
            query = query.filter(Juego.precio <= criterios['precio_max'])
        
        # Filtro por calificación mínima
        if criterios.get('calificacion_min'):
            query = query.filter(Juego.calificacion >= criterios['calificacion_min'])
        
        # Filtro por año de lanzamiento
        if criterios.get('año_lanzamiento'):
            from sqlalchemy import extract
            query = query.filter(
                extract('year', Juego.fecha_lanzamiento) == criterios['año_lanzamiento']
            )
        
        # Búsqueda global (busca en múltiples campos)
        if criterios.get('busqueda_global'):
            termino = f"%{criterios['busqueda_global']}%"
            query = query.filter(
                or_(
                    Juego.nombre.ilike(termino),
                    Juego.genero.ilike(termino),
                    Juego.desarrollador.ilike(termino),
                    Juego.editor.ilike(termino),
                    Juego.descripcion.ilike(termino)
                )
            )
        
        return query
    
    def obtener_por_genero(self, genero: str, page: int = 1, per_page: int = 20) -> Dict:
        """Obtiene juegos filtrados por género"""
        return self.buscar({'genero': genero}, page, per_page)
    
    def obtener_por_plataforma(self, plataforma: str, page: int = 1, per_page: int = 20) -> Dict:
        """Obtiene juegos filtrados por plataforma"""
        return self.buscar({'plataforma': plataforma}, page, per_page)
    
    def obtener_por_desarrollador(self, desarrollador: str, page: int = 1, per_page: int = 20) -> Dict:
        """Obtiene juegos filtrados por desarrollador"""
        return self.buscar({'desarrollador': desarrollador}, page, per_page)
    
    def obtener_mejor_calificados(self, limit: int = 10) -> List[Dict]:
        """Obtiene los juegos mejor calificados"""
        juegos = Juego.query.filter(
            Juego.activo == True,
            Juego.calificacion.isnot(None)
        ).order_by(Juego.calificacion.desc()).limit(limit).all()
        
        return [juego.to_dict() for juego in juegos]
    
    def obtener_mas_recientes(self, limit: int = 10) -> List[Dict]:
        """Obtiene los juegos más recientes"""
        juegos = Juego.query.filter(
            Juego.activo == True,
            Juego.fecha_lanzamiento.isnot(None)
        ).order_by(Juego.fecha_lanzamiento.desc()).limit(limit).all()
        
        return [juego.to_dict() for juego in juegos]
    
    def obtener_por_rango_precio(self, precio_min: float = None, 
                                precio_max: float = None, 
                                page: int = 1, per_page: int = 20) -> Dict:
        """Obtiene juegos por rango de precio"""
        criterios = {}
        if precio_min is not None:
            criterios['precio_min'] = precio_min
        if precio_max is not None:
            criterios['precio_max'] = precio_max
        
        return self.buscar(criterios, page, per_page)
    
    def buscar_global(self, termino: str, page: int = 1, per_page: int = 20) -> Dict:
        """Búsqueda global en múltiples campos"""
        return self.buscar({'busqueda_global': termino}, page, per_page)
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas de los juegos"""
        from sqlalchemy import func
        
        stats = db.session.query(
            func.count(Juego.id).label('total'),
            func.avg(Juego.precio).label('precio_promedio'),
            func.avg(Juego.calificacion).label('calificacion_promedio'),
            func.max(Juego.precio).label('precio_maximo'),
            func.min(Juego.precio).label('precio_minimo')
        ).filter(Juego.activo == True).first()
        
        # Géneros más populares
        generos = db.session.query(
            Juego.genero,
            func.count(Juego.id).label('cantidad')
        ).filter(Juego.activo == True).group_by(Juego.genero).order_by(
            func.count(Juego.id).desc()
        ).limit(5).all()
        
        # Desarrolladores más activos
        desarrolladores = db.session.query(
            Juego.desarrollador,
            func.count(Juego.id).label('cantidad')
        ).filter(Juego.activo == True).group_by(Juego.desarrollador).order_by(
            func.count(Juego.id).desc()
        ).limit(5).all()
        
        return {
            'total_juegos': stats.total or 0,
            'precio_promedio': round(stats.precio_promedio or 0, 2),
            'calificacion_promedio': round(stats.calificacion_promedio or 0, 2),
            'precio_maximo': stats.precio_maximo or 0,
            'precio_minimo': stats.precio_minimo or 0,
            'generos_populares': [{'genero': g.genero, 'cantidad': g.cantidad} for g in generos],
            'desarrolladores_activos': [{'desarrollador': d.desarrollador, 'cantidad': d.cantidad} for d in desarrolladores]
        }

