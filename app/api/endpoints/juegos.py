from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas import Juego, JuegoCreate, JuegoUpdate
from app.crud import crud_juego
from app.database.session import get_db
from app.services.image_processor import process_image
from app.config import settings

router = APIRouter()

@router.post("/", response_model=Juego)
async def create_juego(
    juego: JuegoCreate = Depends(),
    imagen: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # Procesar imagen
    image_data = await imagen.read()
    if len(image_data) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Archivo demasiado grande")
    
    processed = await process_image(image_data, settings)
    
    return await crud_juego.create_juego(
        db=db,
        juego=juego,
        imagen_data=processed['original'],
        thumbnail_data=processed['thumbnail'],
        imagen_type=processed['mime_type']
    )

@router.get("/", response_model=List[Juego])
async def read_juegos(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud_juego.get_juegos(db, skip=skip, limit=limit)

@router.get("/{juego_id}", response_model=Juego)
async def read_juego(juego_id: int, db: AsyncSession = Depends(get_db)):
    db_juego = await crud_juego.get_juego(db, juego_id=juego_id)
    if not db_juego:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    return db_juego

@router.put("/{juego_id}", response_model=Juego)
async def update_juego(
    juego_id: int,
    juego: JuegoUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_juego = await crud_juego.update_juego(db, juego_id=juego_id, juego=juego)
    if not db_juego:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    return db_juego

@router.delete("/{juego_id}", response_model=Juego)
async def delete_juego(juego_id: int, db: AsyncSession = Depends(get_db)):
    db_juego = await crud_juego.delete_juego(db, juego_id=juego_id)
    if not db_juego:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    return db_juego