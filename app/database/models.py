from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, LargeBinary, JSON, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
from typing import Optional

Base = declarative_base()

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
    
    # Campos para almacenamiento de imágenes
    imagen_data = Column(LargeBinary, nullable=False)
    thumbnail_data = Column(LargeBinary, nullable=False)
    imagen_type = Column(String(10), nullable=False)  # MIME type (image/jpeg, etc.)
    
    # Metadata y control
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activo = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    consola = relationship("Consola", back_populates="juegos")
    historiales = relationship("Historial", back_populates="juego", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Juego(id={self.id}, titulo='{self.titulo}')>"


class Consola(Base):
    __tablename__ = "consolas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, index=True, nullable=False)
    fabricante = Column(String(100), nullable=False)
    año_lanzamiento = Column(Integer, nullable=False)
    generacion = Column(Integer, nullable=False)
    precio = Column(Float, nullable=True)
    especificaciones = Column(Text, nullable=True)
    
    # Campos para almacenamiento de imágenes
    imagen_data = Column(LargeBinary, nullable=False)
    thumbnail_data = Column(LargeBinary, nullable=False)
    imagen_type = Column(String(10), nullable=False)
    
    # Metadata y control
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activo = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    juegos = relationship("Juego", back_populates="consola", cascade="all, delete-orphan")
    accesorios = relationship("Accesorio", back_populates="consola", cascade="all, delete-orphan")
    historiales = relationship("Historial", back_populates="consola", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Consola(id={self.id}, nombre='{self.nombre}')>"


class Accesorio(Base):
    __tablename__ = "accesorios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, index=True, nullable=False)
    tipo = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio = Column(Float, nullable=False)
    consola_id = Column(Integer, ForeignKey("consolas.id"), nullable=False)
    
    # Campos para almacenamiento de imágenes
    imagen_data = Column(LargeBinary, nullable=False)
    thumbnail_data = Column(LargeBinary, nullable=False)
    imagen_type = Column(String(10), nullable=False)
    
    # Metadata y control
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activo = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    consola = relationship("Consola", back_populates="accesorios")
    historiales = relationship("Historial", back_populates="accesorio", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Accesorio(id={self.id}, nombre='{self.nombre}')>"


class Historial(Base):
    __tablename__ = "historial"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo_entidad = Column(String(20), nullable=False)  # 'juego', 'consola', 'accesorio'
    entidad_id = Column(Integer, nullable=False)  # ID original del elemento
    accion = Column(String(20), nullable=False)  # 'eliminacion', 'actualizacion', 'creacion'
    datos = Column(JSON, nullable=False)  # JSON con snapshot de los datos
    fecha_accion = Column(DateTime, default=datetime.utcnow, nullable=False)
    usuario = Column(String(50), nullable=True)  # Para futura implementación de auth
    
    # Claves foráneas condicionales
    juego_id = Column(Integer, ForeignKey("juegos.id"), nullable=True)
    consola_id = Column(Integer, ForeignKey("consolas.id"), nullable=True)
    accesorio_id = Column(Integer, ForeignKey("accesorios.id"), nullable=True)
    
    # Relaciones
    juego = relationship("Juego", back_populates="historiales")
    consola = relationship("Consola", back_populates="historiales")
    accesorio = relationship("Accesorio", back_populates="historiales")

    def __repr__(self):
        return f"<Historial(id={self.id}, accion='{self.accion}', entidad='{self.tipo_entidad}')>"


class Catalogo(Base):
    __tablename__ = "catalogos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    
    # Relación muchos-a-muchos con juegos
    juegos = relationship("JuegoCatalogo", back_populates="catalogo")


class JuegoCatalogo(Base):
    __tablename__ = "juego_catalogo"
    
    id = Column(Integer, primary_key=True, index=True)
    juego_id = Column(Integer, ForeignKey("juegos.id"), nullable=False)
    catalogo_id = Column(Integer, ForeignKey("catalogos.id"), nullable=False)
    fecha_agregado = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    juego = relationship("Juego")
    catalogo = relationship("Catalogo", back_populates="juegos")


class Comparacion(Base):
    __tablename__ = "comparaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    usuario = Column(String(50), nullable=True)  # Para futura implementación de auth
    
    # Relaciones (muchos-a-muchos)
    juegos = relationship("ComparacionJuego", back_populates="comparacion")
    consolas = relationship("ComparacionConsola", back_populates="comparacion")
    accesorios = relationship("ComparacionAccesorio", back_populates="comparacion")


class ComparacionJuego(Base):
    __tablename__ = "comparacion_juego"
    
    id = Column(Integer, primary_key=True, index=True)
    comparacion_id = Column(Integer, ForeignKey("comparaciones.id"), nullable=False)
    juego_id = Column(Integer, ForeignKey("juegos.id"), nullable=False)
    comentario = Column(Text, nullable=True)
    
    # Relaciones
    comparacion = relationship("Comparacion", back_populates="juegos")
    juego = relationship("Juego")


# Modelos similares para ComparacionConsola y ComparacionAccesorio
class ComparacionConsola(Base):
    __tablename__ = "comparacion_consola"
    # ... (estructura similar a ComparacionJuego)


class ComparacionAccesorio(Base):
    __tablename__ = "comparacion_accesorio"
    # ... (estructura similar a ComparacionJuego)