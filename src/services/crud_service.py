"""
Servicio CRUD genérico para el sistema de videojuegos
"""
from typing import Dict, List, Optional, Type, Any
from flask import request
from src.models import db, BaseModel, HistorialAccion
from sqlalchemy.exc import SQLAlchemyError

class CRUDService:
    """Servicio CRUD genérico para todos los modelos"""
    
    def __init__(self, model: Type[BaseModel]):
        self.model = model
        self.table_name = model.__tablename__
    
    def crear(self, datos: Dict, usuario: str = 'admin') -> Optional[BaseModel]:
        """Crea un nuevo registro"""
        try:
            # Filtrar campos válidos
            campos_validos = self._filtrar_campos_validos(datos)
            
            # Crear nueva instancia
            nuevo_registro = self.model(**campos_validos)
            db.session.add(nuevo_registro)
            db.session.commit()
            
            # Registrar en historial
            HistorialAccion.registrar_accion(
                tabla=self.table_name,
                registro_id=nuevo_registro.id,
                accion='CREATE',
                datos_nuevos=nuevo_registro.to_dict(),
                usuario=usuario,
                ip_address=self._obtener_ip()
            )
            
            return nuevo_registro
            
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error creando {self.table_name}: {e}")
            return None
    
    def obtener_por_id(self, id: int) -> Optional[BaseModel]:
        """Obtiene un registro por ID"""
        return self.model.query.filter(
            self.model.id == id,
            self.model.activo == True
        ).first()
    
    def obtener_todos(self, page: int = 1, per_page: int = 20, 
                     incluir_inactivos: bool = False) -> Dict:
        """Obtiene todos los registros con paginación"""
        query = self.model.query
        
        if not incluir_inactivos:
            query = query.filter(self.model.activo == True)
        
        # Ordenar por fecha de creación descendente
        query = query.order_by(self.model.fecha_creacion.desc())
        
        # Paginación
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return {
            'items': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    
    def actualizar(self, id: int, datos: Dict, usuario: str = 'admin') -> Optional[BaseModel]:
        """Actualiza un registro existente"""
        try:
            registro = self.obtener_por_id(id)
            if not registro:
                return None
            
            # Guardar estado anterior
            datos_anteriores = registro.to_dict()
            
            # Filtrar campos válidos
            campos_validos = self._filtrar_campos_validos(datos)
            
            # Actualizar campos
            for campo, valor in campos_validos.items():
                if hasattr(registro, campo):
                    setattr(registro, campo, valor)
            
            db.session.commit()
            
            # Registrar en historial
            HistorialAccion.registrar_accion(
                tabla=self.table_name,
                registro_id=registro.id,
                accion='UPDATE',
                datos_anteriores=datos_anteriores,
                datos_nuevos=registro.to_dict(),
                usuario=usuario,
                ip_address=self._obtener_ip()
            )
            
            return registro
            
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error actualizando {self.table_name}: {e}")
            return None
    
    def eliminar(self, id: int, usuario: str = 'admin') -> bool:
        """Elimina un registro (soft delete)"""
        try:
            registro = self.obtener_por_id(id)
            if not registro:
                return False
            
            # Guardar estado anterior
            datos_anteriores = registro.to_dict()
            
            # Soft delete
            registro.activo = False
            db.session.commit()
            
            # Registrar en historial
            HistorialAccion.registrar_accion(
                tabla=self.table_name,
                registro_id=registro.id,
                accion='DELETE',
                datos_anteriores=datos_anteriores,
                datos_nuevos=registro.to_dict(),
                usuario=usuario,
                ip_address=self._obtener_ip()
            )
            
            return True
            
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error eliminando {self.table_name}: {e}")
            return False
    
    def restaurar(self, id: int, usuario: str = 'admin') -> bool:
        """Restaura un registro eliminado"""
        try:
            registro = self.model.query.filter(
                self.model.id == id,
                self.model.activo == False
            ).first()
            
            if not registro:
                return False
            
            # Guardar estado anterior
            datos_anteriores = registro.to_dict()
            
            # Restaurar
            registro.activo = True
            db.session.commit()
            
            # Registrar en historial
            HistorialAccion.registrar_accion(
                tabla=self.table_name,
                registro_id=registro.id,
                accion='RESTORE',
                datos_anteriores=datos_anteriores,
                datos_nuevos=registro.to_dict(),
                usuario=usuario,
                ip_address=self._obtener_ip()
            )
            
            return True
            
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error restaurando {self.table_name}: {e}")
            return False
    
    def buscar(self, criterios: Dict, page: int = 1, per_page: int = 20) -> Dict:
        """Busca registros según criterios específicos"""
        query = self.model.query.filter(self.model.activo == True)
        
        # Aplicar filtros específicos del modelo
        query = self._aplicar_filtros_busqueda(query, criterios)
        
        # Ordenar por relevancia/fecha
        query = query.order_by(self.model.fecha_creacion.desc())
        
        # Paginación
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return {
            'items': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
            'criterios': criterios
        }
    
    def _filtrar_campos_validos(self, datos: Dict) -> Dict:
        """Filtra solo los campos válidos del modelo"""
        campos_validos = {}
        
        # Obtener columnas del modelo
        columnas = [column.name for column in self.model.__table__.columns]
        
        # Excluir campos que no deben ser modificados directamente
        campos_excluidos = ['id', 'fecha_creacion', 'fecha_actualizacion']
        
        for campo, valor in datos.items():
            if campo in columnas and campo not in campos_excluidos:
                campos_validos[campo] = valor
        
        return campos_validos
    
    def _aplicar_filtros_busqueda(self, query, criterios: Dict):
        """Aplica filtros de búsqueda específicos del modelo (debe ser sobrescrito)"""
        return query
    
    def _obtener_ip(self) -> str:
        """Obtiene la IP del cliente"""
        try:
            return request.environ.get('HTTP_X_FORWARDED_FOR', 
                                     request.environ.get('REMOTE_ADDR', 'unknown'))
        except:
            return 'unknown'

