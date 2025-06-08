from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from app import schemas, crud
from app.api.deps import get_db
from app.models.juego import Juego

router = APIRouter()

@router.post("/", response_model=schemas.Juego)
async def create_juego(
    juego: schemas.JuegoCreate = Depends(),
    imagen: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo juego con imagen.
    """
    return await crud.create_juego(db=db, juego=juego, imagen=imagen)

@router.put("/{juego_id}", response_model=schemas.Juego)
async def update_juego(
    juego_id: int,
    juego: schemas.JuegoUpdate = Depends(),
    imagen: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """
    Actualizar un juego (imagen opcional).
    """
    return await crud.update_juego(db=db, juego_id=juego_id, juego=juego, imagen=imagen)