from fastapi import FastAPI
from app.config import settings
from app.api.endpoints import juegos, historial, images

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

# Incluir routers
app.include_router(juegos.router, prefix="/juegos", tags=["juegos"])
app.include_router(historial.router, prefix="/historial", tags=["historial"])
app.include_router(images.router, prefix="/images", tags=["images"])

@app.get("/")
def read_root():
    return {"message": "Sistema de gestión de videojuegos"}