"""
Servicio específico para el modelo Consolas
"""
from typing import Dict, List
from sqlalchemy import or_, and_
from src.services.crud_service import CRUDService
from src.models.consolas import Consola
from src.models import db

class ConsolasService(CRUDService):
    """Servicio específico para gestión de consolas"""
    
    def __init__(self):
        super().__init__(Consola)
    
    def _aplicar_filtros_busqueda(self, query, criterios: Dict):
        """Aplica filtros de búsqueda específicos para consolas"""
        
        # Búsqueda por nombre
        if criterios.get('nombre'):
            query = query.filter(
                Consola.nombre.ilike(f"%{criterios['nombre']}%")
            )
        
        # Filtro por fabricante
        if criterios.get('fabricante'):
            query = query.filter(
                Consola.fabricante.ilike(f"%{criterios['fabricante']}%")
            )
        
        # Filtro por tipo
        if criterios.get('tipo'):
            query = query.filter(
                Consola.tipo.ilike(f"%{criterios['tipo']}%")
            )
        
        # Filtro por generación
        if criterios.get('generacion'):
            query = query.filter(Consola.generacion == criterios['generacion'])
        
        # Filtro por rango de precio
        if criterios.get('precio_min'):
            query = query.filter(Consola.precio >= criterios['precio_min'])
        
        if criterios.get('precio_max'):
            query = query.filter(Consola.precio <= criterios['precio_max'])
        
        # Filtro por año de lanzamiento
        if criterios.get('año_lanzamiento'):
            from sqlalchemy import extract
            query = query.filter(
                extract('year', Consola.fecha_lanzamiento) == criterios['año_lanzamiento']
            )
        
        # Búsqueda global (busca en múltiples campos)
        if criterios.get('busqueda_global'):
            termino = f"%{criterios['busqueda_global']}%"
            query = query.filter(
                or_(
                    Consola.nombre.ilike(termino),
                    Consola.fabricante.ilike(termino),
                    Consola.tipo.ilike(termino),
                    Consola.procesador.ilike(termino),
                    Consola.descripcion.ilike(termino)
                )
            )
        
        return query
    
    def obtener_por_fabricante(self, fabricante: str, page: int = 1, per_page: int = 20) -> Dict:
        """Obtiene consolas filtradas por fabricante"""
        return self.buscar({'fabricante': fabricante}, page, per_page)
    
    def obtener_por_tipo(self, tipo: str, page: int = 1, per_page: int = 20) -> Dict:
        """Obtiene consolas filtradas por tipo"""
        return self.buscar({'tipo': tipo}, page, per_page)
    
    def obtener_por_generacion(self, generacion: int, page: int = 1, per_page: int = 20) -> Dict:
        """Obtiene consolas filtradas por generación"""
        return self.buscar({'generacion': generacion}, page, per_page)
    
    def obtener_mas_recientes(self, limit: int = 10) -> List[Dict]:
        """Obtiene las consolas más recientes"""
        consolas = Consola.query.filter(
            Consola.activo == True,
            Consola.fecha_lanzamiento.isnot(None)
        ).order_by(Consola.fecha_lanzamiento.desc()).limit(limit).all()
        
        return [consola.to_dict() for consola in consolas]
    
    def obtener_por_rango_precio(self, precio_min: float = None, 
                                precio_max: float = None, 
                                page: int = 1, per_page: int = 20) -> Dict:
        """Obtiene consolas por rango de precio"""
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
        """Obtiene estadísticas de las consolas"""
        from sqlalchemy import func
        
        stats = db.session.query(
            func.count(Consola.id).label('total'),
            func.avg(Consola.precio).label('precio_promedio'),
            func.max(Consola.precio).label('precio_maximo'),
            func.min(Consola.precio).label('precio_minimo')
        ).filter(Consola.activo == True).first()
        
        # Fabricantes más populares
        fabricantes = db.session.query(
            Consola.fabricante,
            func.count(Consola.id).label('cantidad')
        ).filter(Consola.activo == True).group_by(Consola.fabricante).order_by(
            func.count(Consola.id).desc()
        ).limit(5).all()
        
        # Tipos más populares
        tipos = db.session.query(
            Consola.tipo,
            func.count(Consola.id).label('cantidad')
        ).filter(Consola.activo == True).group_by(Consola.tipo).order_by(
            func.count(Consola.id).desc()
        ).limit(5).all()
        
        # Generaciones
        generaciones = db.session.query(
            Consola.generacion,
            func.count(Consola.id).label('cantidad')
        ).filter(Consola.activo == True).group_by(Consola.generacion).order_by(
            Consola.generacion.desc()
        ).limit(5).all()
        
        return {
            'total_consolas': stats.total or 0,
            'precio_promedio': round(stats.precio_promedio or 0, 2),
            'precio_maximo': stats.precio_maximo or 0,
            'precio_minimo': stats.precio_minimo or 0,
            'fabricantes_populares': [{'fabricante': f.fabricante, 'cantidad': f.cantidad} for f in fabricantes],
            'tipos_populares': [{'tipo': t.tipo, 'cantidad': t.cantidad} for t in tipos],
            'generaciones': [{'generacion': g.generacion, 'cantidad': g.cantidad} for g in generaciones]
        }

