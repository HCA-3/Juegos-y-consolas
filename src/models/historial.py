"""
Modelo de Historial de Acciones para auditoría del sistema
"""
from src.models.database import db
from datetime import datetime
import json

class HistorialAccion(db.Model):
    __tablename__ = 'historial_acciones'
    
    id = db.Column(db.Integer, primary_key=True)
    tabla_afectada = db.Column(db.String(50), nullable=False)
    registro_id = db.Column(db.Integer, nullable=False)
    accion = db.Column(db.String(20), nullable=False)  # CREATE, UPDATE, DELETE
    datos_anteriores = db.Column(db.Text, nullable=True)  # JSON string
    datos_nuevos = db.Column(db.Text, nullable=True)  # JSON string
    usuario = db.Column(db.String(100), default='admin', nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<HistorialAccion {self.accion} en {self.tabla_afectada}>'
    
    def to_dict(self):
        """Convierte el modelo a diccionario"""
        return {
            'id': self.id,
            'tabla_afectada': self.tabla_afectada,
            'registro_id': self.registro_id,
            'accion': self.accion,
            'datos_anteriores': json.loads(self.datos_anteriores) if self.datos_anteriores else None,
            'datos_nuevos': json.loads(self.datos_nuevos) if self.datos_nuevos else None,
            'usuario': self.usuario,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def registrar_accion(cls, tabla, registro_id, accion, datos_anteriores=None, datos_nuevos=None, usuario='admin', ip_address=None):
        """Registra una nueva acción en el historial"""
        historial = cls(
            tabla_afectada=tabla,
            registro_id=registro_id,
            accion=accion,
            datos_anteriores=json.dumps(datos_anteriores) if datos_anteriores else None,
            datos_nuevos=json.dumps(datos_nuevos) if datos_nuevos else None,
            usuario=usuario,
            ip_address=ip_address
        )
        
        db.session.add(historial)
        db.session.commit()
        return historial
    
    @classmethod
    def obtener_por_tabla(cls, tabla):
        """Obtiene el historial de una tabla específica"""
        return cls.query.filter(cls.tabla_afectada == tabla).order_by(cls.timestamp.desc()).all()
    
    @classmethod
    def obtener_por_registro(cls, tabla, registro_id):
        """Obtiene el historial de un registro específico"""
        return cls.query.filter(
            cls.tabla_afectada == tabla,
            cls.registro_id == registro_id
        ).order_by(cls.timestamp.desc()).all()
    
    @classmethod
    def obtener_por_accion(cls, accion):
        """Obtiene el historial por tipo de acción"""
        return cls.query.filter(cls.accion == accion).order_by(cls.timestamp.desc()).all()
    
    @classmethod
    def obtener_por_fecha(cls, fecha_inicio=None, fecha_fin=None):
        """Obtiene el historial por rango de fechas"""
        query = cls.query
        
        if fecha_inicio:
            query = query.filter(cls.timestamp >= fecha_inicio)
        if fecha_fin:
            query = query.filter(cls.timestamp <= fecha_fin)
            
        return query.order_by(cls.timestamp.desc()).all()
    
    @classmethod
    def obtener_todos(cls, limit=100):
        """Obtiene todo el historial con límite"""
        return cls.query.order_by(cls.timestamp.desc()).limit(limit).all()

