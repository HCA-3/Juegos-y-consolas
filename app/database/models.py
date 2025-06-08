from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, LargeBinary, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class Juego(Base):
    __tablename__ = "juegos"
    
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100), unique=True, index=True, nullable=False)
    desarrollador = Column(String(100), nullable=False)
    genero = Column(String(50), nullable=False)
    año_lanzamiento = Column(Integer, nullable=False)
    precio = Column(Float, nullable=False)
    descripcion = Column(Text, nullable=True)
    consola_id = Column(Integer, ForeignKey("consolas.id"), nullable=False)
    
    # Campos para imágenes
    imagen_data = Column(LargeBinary, nullable=False)
    thumbnail_data = Column(LargeBinary, nullable=False)
    imagen_type = Column(String(10), nullable=False)
    
    # Metadata
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activo = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    consola = relationship("Consola", back_populates="juegos")
    historiales = relationship("Historial", back_populates="juego")

class Consola(Base):
    __tablename__ = "consolas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, index=True, nullable=False)
    fabricante = Column(String(100), nullable=False)
    año_lanzamiento = Column(Integer, nullable=False)
    generacion = Column(Integer, nullable=False)
    precio = Column(Float, nullable=True)
    especificaciones = Column(Text, nullable=True)
    
    # Campos para imágenes
    imagen_data = Column(LargeBinary, nullable=False)
    thumbnail_data = Column(LargeBinary, nullable=False)
    imagen_type = Column(String(10), nullable=False)
    
    # Metadata
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activo = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    juegos = relationship("Juego", back_populates="consola")
    accesorios = relationship("Accesorio", back_populates="consola")
    historiales = relationship("Historial", back_populates="consola")

class Accesorio(Base):
    __tablename__ = "accesorios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, index=True, nullable=False)
    tipo = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio = Column(Float, nullable=False)
    consola_id = Column(Integer, ForeignKey("consolas.id"), nullable=False)
    
    # Campos para imágenes
    imagen_data = Column(LargeBinary, nullable=False)
    thumbnail_data = Column(LargeBinary, nullable=False)
    imagen_type = Column(String(10), nullable=False)
    
    # Metadata
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activo = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    consola = relationship("Consola", back_populates="accesorios")
    historiales = relationship("Historial", back_populates="accesorio")

class Historial(Base):
    __tablename__ = "historial"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo_entidad = Column(String(20), nullable=False)
    entidad_id = Column(Integer, nullable=False)
    accion = Column(String(20), nullable=False)
    datos = Column(Text, nullable=False)
    fecha_accion = Column(DateTime, default=datetime.utcnow, nullable=False)
    usuario = Column(String(50), nullable=True)
    
    # Claves foráneas
    juego_id = Column(Integer, ForeignKey("juegos.id"), nullable=True)
    consola_id = Column(Integer, ForeignKey("consolas.id"), nullable=True)
    accesorio_id = Column(Integer, ForeignKey("accesorios.id"), nullable=True)
    
    # Relaciones
    juego = relationship("Juego", back_populates="historiales")
    consola = relationship("Consola", back_populates="historiales")
    accesorio = relationship("Accesorio", back_populates="historiales")