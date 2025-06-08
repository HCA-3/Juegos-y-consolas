from io import BytesIO
from PIL import Image
import imghdr
from fastapi import HTTPException

async def process_image(file_data: bytes, config) -> dict:
    # Validar tipo de imagen
    image_type = imghdr.what(None, h=file_data)
    if image_type not in ['jpeg', 'png', 'gif']:
        raise HTTPException(status_code=400, detail="Formato de imagen no soportado")
    
    try:
        img = Image.open(BytesIO(file_data))
        
        # Redimensionar si es necesario
        if img.width > config.IMAGE_MAX_WIDTH or img.height > config.IMAGE_MAX_HEIGHT:
            img.thumbnail((config.IMAGE_MAX_WIDTH, config.IMAGE_MAX_HEIGHT))
        
        # Crear miniatura
        thumb = img.copy()
        thumb.thumbnail(config.THUMBNAIL_SIZE)
        
        # Convertir a bytes
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format=image_type)
        
        thumb_byte_arr = BytesIO()
        thumb.save(thumb_byte_arr, format=image_type)
        
        return {
            'original': img_byte_arr.getvalue(),
            'thumbnail': thumb_byte_arr.getvalue(),
            'mime_type': f'image/{image_type}'
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error procesando imagen: {str(e)}")