import os
from pathlib import Path
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Configuración básica de la aplicación
    PROJECT_NAME: str = "Sistema de Gestión de Videojuegos"
    PROJECT_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Configuración de la base de datos
    DATABASE_URL: str = "sqlite:///./videojuegos.db"
    DATABASE_TEST_URL: str = "sqlite:///./test_videojuegos.db"
    
    # Configuración de imágenes
    IMAGE_UPLOAD_FOLDER: str = "static/uploads"
    ALLOWED_IMAGE_EXTENSIONS: set = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_IMAGE_SIZE: int = 5 * 1024 * 1024  # 5MB
    IMAGE_MAX_WIDTH: int = 1920
    IMAGE_MAX_HEIGHT: int = 1080
    THUMBNAIL_WIDTH: int = 300
    THUMBNAIL_HEIGHT: int = 300
    
    # Configuración de seguridad (opcional para futura implementación)
    SECRET_KEY: str = "secret-key-para-firmar-tokens"  # Cambiar en producción
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Configuración de directorios
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    STATIC_DIR: Path = BASE_DIR / "static"
    TEMPLATE_DIR: Path = BASE_DIR / "templates"
    UPLOAD_DIR: Path = BASE_DIR / IMAGE_UPLOAD_FOLDER
    
    # Configuración del servidor
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    SERVER_RELOAD: bool = True
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_dirs()
    
    def create_dirs(self):
        """Crea los directorios necesarios si no existen"""
        os.makedirs(self.STATIC_DIR, exist_ok=True)
        os.makedirs(self.TEMPLATE_DIR, exist_ok=True)
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
    
    @property
    def thumbnail_size(self) -> tuple:
        return (self.THUMBNAIL_WIDTH, self.THUMBNAIL_HEIGHT)
    
    @property
    def database_config(self) -> dict:
        return {
            "url": self.DATABASE_URL,
            "pool_pre_ping": True,
            "pool_size": 5,
            "max_overflow": 10,
            "echo": self.DEBUG
        }
    
    @property
    def test_database_config(self) -> dict:
        return {
            "url": self.DATABASE_TEST_URL,
            "pool_pre_ping": True,
            "pool_size": 5,
            "max_overflow": 10,
            "echo": False
        }

# Instancia de configuración global
settings = Settings()

# Configuración para testing
class TestSettings(Settings):
    DATABASE_URL: str = settings.DATABASE_TEST_URL
    DEBUG: bool = True
    SERVER_RELOAD: bool = False

test_settings = TestSettings()