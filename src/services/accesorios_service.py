"""
Servicio específico para el modelo Accesorios
"""
from typing import Dict, List
from sqlalchemy import or_, and_
from src.services.crud_service import CRUDService
from src.models.accesorios import Accesorio
from src.models import db

class AccesoriosService(CRUDService):
    """Servicio específico para gestión de accesorios"""
    
    def __init__(self):
        super().__init__(Accesorio)
    
    def _aplicar_filtros_busqueda(self, query, criterios: Dict):
        """Aplica filtros de búsqueda específicos para accesorios"""
        
        # Búsqueda por nombre
        if criterios.get('nombre'):
            query = query.filter(
                Accesorio.nombre.ilike(f"%{criterios['nombre']}%")
            )
        
        # Filtro por tipo
        if criterios.get('tipo'):
            query = query.filter(
                Accesorio.tipo.ilike(f"%{criterios['tipo']}%")
            )
        
        # Filtro por fabricante
        if criterios.get('fabricante'):
            query = query.filter(
                Accesorio.fabricante.ilike(f"%{criterios['fabricante']}%")
            )
        
        # Filtro por compatibilidad
        if criterios.get('compatibilidad'):
            query = query.filter(
                Accesorio.compatibilidad.ilike(f"%{criterios['compatibilidad']}%")
            )
        
        # Filtro por rango de precio
        if criterios.get('precio_min'):
            query = query.filter(Accesorio.precio >= criterios['precio_min'])
        
        if criterios.get('precio_max'):
            query = query.filter(Accesorio.precio <= criterios['precio_max'])
        
        # Filtro por año de lanzamiento
        if criterios.get('año_lanzamiento'):
            from sqlalchemy import extract
            query = query.filter(
                extract('year', Accesorio.fecha_lanzamiento) == criterios['año_lanzamiento']
            )
        
        # Búsqueda global (busca en múltiples campos)
        if criterios.get('busqueda_global'):
            termino = f"%{criterios['busqueda_global']}%"
            query = query.filter(
                or_(
                    Accesorio.nombre.ilike(termino),
                    Accesorio.tipo.ilike(termino),
                    Accesorio.fabricante.ilike(termino),
                    Accesorio.compatibilidad.ilike(termino),
                    Accesorio.descripcion.ilike(termino)
                )
            )
        
        return query
    
    def obtener_por_tipo(self, tipo: str, page: int = 1, per_page: int = 20) -> Dict:
        """Obtiene accesorios filtrados por tipo"""
        return self.buscar({'tipo': tipo}, page, per_page)
    
    def obtener_por_fabricante(self, fabricante: str, page: int = 1, per_page: int = 20) -> Dict:
        """Obtiene accesorios filtrados por fabricante"""
        return self.buscar({'fabricante': fabricante}, page, per_page)
    
    def obtener_por_compatibilidad(self, compatibilidad: str, page: int = 1, per_page: int = 20) -> Dict:
        """Obtiene accesorios filtrados por compatibilidad"""
        return self.buscar({'compatibilidad': compatibilidad}, page, per_page)
    
    def obtener_mas_recientes(self, limit: int = 10) -> List[Dict]:
        """Obtiene los accesorios más recientes"""
        accesorios = Accesorio.query.filter(
            Accesorio.activo == True,
            Accesorio.fecha_lanzamiento.isnot(None)
        ).order_by(Accesorio.fecha_lanzamiento.desc()).limit(limit).all()
        
        return [accesorio.to_dict() for accesorio in accesorios]
    
    def obtener_por_rango_precio(self, precio_min: float = None, 
                                precio_max: float = None, 
                                page: int = 1, per_page: int = 20) -> Dict:
        """Obtiene accesorios por rango de precio"""
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
        """Obtiene estadísticas de los accesorios"""
        from sqlalchemy import func
        
        stats = db.session.query(
            func.count(Accesorio.id).label('total'),
            func.avg(Accesorio.precio).label('precio_promedio'),
            func.max(Accesorio.precio).label('precio_maximo'),
            func.min(Accesorio.precio).label('precio_minimo')
        ).filter(Accesorio.activo == True).first()
        
        # Tipos más populares
        tipos = db.session.query(
            Accesorio.tipo,
            func.count(Accesorio.id).label('cantidad')
        ).filter(Accesorio.activo == True).group_by(Accesorio.tipo).order_by(
            func.count(Accesorio.id).desc()
        ).limit(5).all()
        
        # Fabricantes más populares
        fabricantes = db.session.query(
            Accesorio.fabricante,
            func.count(Accesorio.id).label('cantidad')
        ).filter(Accesorio.activo == True).group_by(Accesorio.fabricante).order_by(
            func.count(Accesorio.id).desc()
        ).limit(5).all()
        
        # Compatibilidades más comunes
        compatibilidades = db.session.query(
            Accesorio.compatibilidad,
            func.count(Accesorio.id).label('cantidad')
        ).filter(Accesorio.activo == True).group_by(Accesorio.compatibilidad).order_by(
            func.count(Accesorio.id).desc()
        ).limit(5).all()
        
        return {
            'total_accesorios': stats.total or 0,
            'precio_promedio': round(stats.precio_promedio or 0, 2),
            'precio_maximo': stats.precio_maximo or 0,
            'precio_minimo': stats.precio_minimo or 0,
            'tipos_populares': [{'tipo': t.tipo, 'cantidad': t.cantidad} for t in tipos],
            'fabricantes_populares': [{'fabricante': f.fabricante, 'cantidad': f.cantidad} for f in fabricantes],
            'compatibilidades_comunes': [{'compatibilidad': c.compatibilidad, 'cantidad': c.cantidad} for c in compatibilidades]
        }

