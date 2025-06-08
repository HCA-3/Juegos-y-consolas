from sqlalchemy.orm import Session
from app.models.historial import Historial
from datetime import datetime
import json

def create_historial_entry(
    db: Session,
    tipo_entidad: str,
    entidad_id: int,
    datos: dict,
    eliminado_por: str = "sistema"
) -> Historial:
    db_historial = Historial(
        tipo_entidad=tipo_entidad,
        entidad_id=entidad_id,
        datos=json.dumps(datos),
        eliminado_por=eliminado_por
    )
    db.add(db_historial)
    db.commit()
    db.refresh(db_historial)
    return db_historial

def get_historial(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Historial)\
        .order_by(Historial.fecha_eliminacion.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()