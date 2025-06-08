"""
Modelo de Juegos para el sistema de gestión de videojuegos
"""
from src.models.database import db, BaseModel

class Juego(BaseModel):
    __tablename__ = 'juegos'
    
    nombre = db.Column(db.String(200), nullable=False)
    genero = db.Column(db.String(100), nullable=False)
    plataforma = db.Column(db.String(200), nullable=False)
    desarrollador = db.Column(db.String(150), nullable=False)
    editor = db.Column(db.String(150), nullable=True)
    fecha_lanzamiento = db.Column(db.Date, nullable=True)
    precio = db.Column(db.Float, nullable=True)
    calificacion = db.Column(db.Float, nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    imagen_url = db.Column(db.String(500), nullable=True)
    api_id = db.Column(db.String(100), nullable=True)  # ID de API externa
    
    def __repr__(self):
        return f'<Juego {self.nombre}>'
    
    def to_dict(self):
        """Convierte el modelo a diccionario con formato específico"""
        data = super().to_dict()
        if self.fecha_lanzamiento:
            data['fecha_lanzamiento'] = self.fecha_lanzamiento.isoformat()
        return data
    
    @classmethod
    def buscar_por_nombre(cls, nombre):
        """Busca juegos por nombre (búsqueda parcial)"""
        return cls.query.filter(
            cls.nombre.ilike(f'%{nombre}%'),
            cls.activo == True
        ).all()
    
    @classmethod
    def buscar_por_genero(cls, genero):
        """Busca juegos por género"""
        return cls.query.filter(
            cls.genero.ilike(f'%{genero}%'),
            cls.activo == True
        ).all()
    
    @classmethod
    def buscar_por_desarrollador(cls, desarrollador):
        """Busca juegos por desarrollador"""
        return cls.query.filter(
            cls.desarrollador.ilike(f'%{desarrollador}%'),
            cls.activo == True
        ).all()
    
    @classmethod
    def buscar_por_precio(cls, precio_min=None, precio_max=None):
        """Busca juegos por rango de precio"""
        query = cls.query.filter(cls.activo == True)
        
        if precio_min is not None:
            query = query.filter(cls.precio >= precio_min)
        if precio_max is not None:
            query = query.filter(cls.precio <= precio_max)
            
        return query.all()
    
    @classmethod
    def obtener_activos(cls):
        """Obtiene todos los juegos activos"""
        return cls.query.filter(cls.activo == True).all()
    
    @classmethod
    def obtener_por_id(cls, id):
        """Obtiene un juego por ID si está activo"""
        return cls.query.filter(cls.id == id, cls.activo == True).first()

