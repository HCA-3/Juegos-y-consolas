from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models import Juego, Historial
from app.schemas import JuegoCreate, JuegoUpdate
from datetime import datetime
import json

async def create_juego(db: AsyncSession, juego: JuegoCreate, imagen_data: bytes, thumbnail_data: bytes, imagen_type: str):
    db_juego = Juego(
        **juego.model_dump(),
        imagen_data=imagen_data,
        thumbnail_data=thumbnail_data,
        imagen_type=imagen_type
    )
    db.add(db_juego)
    await db.commit()
    await db.refresh(db_juego)
    
    # Registrar en historial
    historial = Historial(
        tipo_entidad="juego",
        entidad_id=db_juego.id,
        accion="creacion",
        datos=json.dumps(juego.model_dump()),
        juego_id=db_juego.id
    )
    db.add(historial)
    await db.commit()
    
    return db_juego

async def get_juego(db: AsyncSession, juego_id: int):
    result = await db.execute(select(Juego).filter(Juego.id == juego_id))
    return result.scalars().first()

async def get_juegos(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Juego).offset(skip).limit(limit))
    return result.scalars().all()

async def update_juego(db: AsyncSession, juego_id: int, juego: JuegoUpdate):
    db_juego = await get_juego(db, juego_id)
    if not db_juego:
        return None
    
    update_data = juego.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_juego, key, value)
    
    db_juego.fecha_actualizacion = datetime.utcnow()
    await db.commit()
    await db.refresh(db_juego)
    
    # Registrar en historial
    historial = Historial(
        tipo_entidad="juego",
        entidad_id=db_juego.id,
        accion="actualizacion",
        datos=json.dumps(update_data),
        juego_id=db_juego.id
    )
    db.add(historial)
    await db.commit()
    
    return db_juego

async def delete_juego(db: AsyncSession, juego_id: int):
    db_juego = await get_juego(db, juego_id)
    if not db_juego:
        return None
    
    db_juego.activo = False
    await db.commit()
    
    # Registrar en historial
    historial = Historial(
        tipo_entidad="juego",
        entidad_id=db_juego.id,
        accion="eliminacion",
        datos=json.dumps({
            "titulo": db_juego.titulo,
            "desarrollador": db_juego.desarrollador,
            "precio": db_juego.precio
        }),
        juego_id=db_juego.id
    )
    db.add(historial)
    await db.commit()
    
    return db_juego