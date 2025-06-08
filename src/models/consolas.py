"""
Modelo de Consolas para el sistema de gestión de videojuegos
"""
from src.models.database import db, BaseModel

class Consola(BaseModel):
    __tablename__ = 'consolas'
    
    nombre = db.Column(db.String(200), nullable=False)
    fabricante = db.Column(db.String(100), nullable=False)
    generacion = db.Column(db.Integer, nullable=True)
    fecha_lanzamiento = db.Column(db.Date, nullable=True)
    precio = db.Column(db.Float, nullable=True)
    tipo = db.Column(db.String(50), nullable=False)  # sobremesa, portátil, híbrida
    almacenamiento = db.Column(db.String(100), nullable=True)
    procesador = db.Column(db.String(200), nullable=True)
    memoria = db.Column(db.String(100), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    imagen_url = db.Column(db.String(500), nullable=True)
    api_id = db.Column(db.String(100), nullable=True)  # ID de API externa
    
    def __repr__(self):
        return f'<Consola {self.nombre}>'
    
    def to_dict(self):
        """Convierte el modelo a diccionario con formato específico"""
        data = super().to_dict()
        if self.fecha_lanzamiento:
            data['fecha_lanzamiento'] = self.fecha_lanzamiento.isoformat()
        return data
    
    @classmethod
    def buscar_por_nombre(cls, nombre):
        """Busca consolas por nombre (búsqueda parcial)"""
        return cls.query.filter(
            cls.nombre.ilike(f'%{nombre}%'),
            cls.activo == True
        ).all()
    
    @classmethod
    def buscar_por_fabricante(cls, fabricante):
        """Busca consolas por fabricante"""
        return cls.query.filter(
            cls.fabricante.ilike(f'%{fabricante}%'),
            cls.activo == True
        ).all()
    
    @classmethod
    def buscar_por_tipo(cls, tipo):
        """Busca consolas por tipo"""
        return cls.query.filter(
            cls.tipo.ilike(f'%{tipo}%'),
            cls.activo == True
        ).all()
    
    @classmethod
    def buscar_por_generacion(cls, generacion):
        """Busca consolas por generación"""
        return cls.query.filter(
            cls.generacion == generacion,
            cls.activo == True
        ).all()
    
    @classmethod
    def buscar_por_precio(cls, precio_min=None, precio_max=None):
        """Busca consolas por rango de precio"""
        query = cls.query.filter(cls.activo == True)
        
        if precio_min is not None:
            query = query.filter(cls.precio >= precio_min)
        if precio_max is not None:
            query = query.filter(cls.precio <= precio_max)
            
        return query.all()
    
    @classmethod
    def obtener_activos(cls):
        """Obtiene todas las consolas activas"""
        return cls.query.filter(cls.activo == True).all()
    
    @classmethod
    def obtener_por_id(cls, id):
        """Obtiene una consola por ID si está activa"""
        return cls.query.filter(cls.id == id, cls.activo == True).first()

