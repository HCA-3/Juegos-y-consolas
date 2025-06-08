"""
Modelo de Accesorios para el sistema de gestión de videojuegos
"""
from src.models.database import db, BaseModel

class Accesorio(BaseModel):
    __tablename__ = 'accesorios'
    
    nombre = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(100), nullable=False)  # control, auriculares, teclado, etc.
    consola_compatible = db.Column(db.String(300), nullable=True)  # Lista de consolas compatibles
    fabricante = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=True)
    conectividad = db.Column(db.String(100), nullable=True)  # inalámbrico, USB, Bluetooth, etc.
    descripcion = db.Column(db.Text, nullable=True)
    imagen_url = db.Column(db.String(500), nullable=True)
    
    def __repr__(self):
        return f'<Accesorio {self.nombre}>'
    
    @classmethod
    def buscar_por_nombre(cls, nombre):
        """Busca accesorios por nombre (búsqueda parcial)"""
        return cls.query.filter(
            cls.nombre.ilike(f'%{nombre}%'),
            cls.activo == True
        ).all()
    
    @classmethod
    def buscar_por_tipo(cls, tipo):
        """Busca accesorios por tipo"""
        return cls.query.filter(
            cls.tipo.ilike(f'%{tipo}%'),
            cls.activo == True
        ).all()
    
    @classmethod
    def buscar_por_fabricante(cls, fabricante):
        """Busca accesorios por fabricante"""
        return cls.query.filter(
            cls.fabricante.ilike(f'%{fabricante}%'),
            cls.activo == True
        ).all()
    
    @classmethod
    def buscar_por_consola_compatible(cls, consola):
        """Busca accesorios compatibles con una consola"""
        return cls.query.filter(
            cls.consola_compatible.ilike(f'%{consola}%'),
            cls.activo == True
        ).all()
    
    @classmethod
    def buscar_por_precio(cls, precio_min=None, precio_max=None):
        """Busca accesorios por rango de precio"""
        query = cls.query.filter(cls.activo == True)
        
        if precio_min is not None:
            query = query.filter(cls.precio >= precio_min)
        if precio_max is not None:
            query = query.filter(cls.precio <= precio_max)
            
        return query.all()
    
    @classmethod
    def obtener_activos(cls):
        """Obtiene todos los accesorios activos"""
        return cls.query.filter(cls.activo == True).all()
    
    @classmethod
    def obtener_por_id(cls, id):
        """Obtiene un accesorio por ID si está activo"""
        return cls.query.filter(cls.id == id, cls.activo == True).first()

