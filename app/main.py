from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.api.endpoints import juegos, consolas, accesorios, historial, images
from app.database.session import engine, Base

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir routers
app.include_router(juegos.router, prefix="/api/juegos", tags=["juegos"])
app.include_router(consolas.router, prefix="/api/consolas", tags=["consolas"])
app.include_router(accesorios.router, prefix="/api/accesorios", tags=["accesorios"])
app.include_router(historial.router, prefix="/api/historial", tags=["historial"])
app.include_router(images.router, prefix="/api/images", tags=["images"])

@app.on_event("startup")
async def startup():
    # Crear tablas de la base de datos
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "Bienvenido al sistema de gestión de videojuegos"}