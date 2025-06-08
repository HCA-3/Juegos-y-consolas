import os
from fastapi import UploadFile, HTTPException
from app.config import settings
from datetime import datetime
import uuid

def allowed_file(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_EXTENSIONS

async def save_upload_file(upload_file: UploadFile) -> str:
    # Validar extensión
    if not allowed_file(upload_file.filename):
        raise HTTPException(
            status_code=400, 
            detail="Formato de archivo no permitido. Use: .png, .jpg, .jpeg o .gif"
        )
    
    # Validar tamaño
    contents = await upload_file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Archivo demasiado grande. Tamaño máximo: {settings.MAX_FILE_SIZE/1024/1024}MB"
        )
    
    # Generar nombre único para el archivo
    file_ext = upload_file.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # Guardar el archivo
    with open(file_path, "wb") as f:
        f.write(contents)
    
    return f"/{settings.UPLOAD_FOLDER}/{unique_filename}"