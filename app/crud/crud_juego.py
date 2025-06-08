async def delete_juego(db: Session, juego_id: int):
    db_juego = db.query(Juego).filter(Juego.id == juego_id).first()
    if not db_juego:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    
    # Crear entrada en el historial antes de "eliminar"
    from app.crud import crud_historial
    crud_historial.create_historial_entry(
        db,
        tipo_entidad="juego",
        entidad_id=juego_id,
        datos={
            "titulo": db_juego.titulo,
            "desarrollador": db_juego.desarrollador,
            "genero": db_juego.genero,
            "año_lanzamiento": db_juego.año_lanzamiento,
            "precio": db_juego.precio,
            "consola_id": db_juego.consola_id
        }
    )
    
    # Eliminación lógica
    db_juego.activo = False
    db.commit()
    return db_juego