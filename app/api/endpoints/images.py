from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models import Juego, Consola, Accesorio

router = APIRouter()

@router.get("/juegos/{juego_id}/image")
async def get_juego_image(
    juego_id: int,
    thumbnail: bool = False,
    db: Session = Depends(get_db)
):
    juego = db.query(Juego).filter(Juego.id == juego_id).first()
    if not juego:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    
    image_data = juego.thumbnail_data if thumbnail else juego.imagen_data
    return Response(
        content=image_data,
        media_type=juego.imagen_type
    )

# Endpoints similares para consolas y accesorios...