from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app import schemas
from app.api.deps import get_db
from app.crud import crud_historial

router = APIRouter()

@router.get("/", response_model=List[schemas.Historial])
def read_historial(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud_historial.get_historial(db, skip=skip, limit=limit)