"""
Script de prueba para verificar el funcionamiento del backend
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
from src.models import db, Juego, Consola, Accesorio, HistorialAccion
from src.services.juegos_service import JuegosService
from src.api.api_manager import APIManager

def test_database():
    """Prueba la conexión y creación de la base de datos"""
    print("=== Probando Base de Datos ===")
    
    # Crear aplicación Flask temporal
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_videojuegos.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        try:
            # Crear tablas
            db.create_all()
            print("✓ Base de datos creada correctamente")
            
            # Verificar que las tablas existen
            tables = db.engine.table_names()
            print(f"✓ Tablas creadas: {tables}")
            
            return True
        except Exception as e:
            print(f"✗ Error creando base de datos: {e}")
            return False

def test_juegos_service():
    """Prueba el servicio de juegos"""
    print("\n=== Probando Servicio de Juegos ===")
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_videojuegos.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        try:
            service = JuegosService()
            
            # Crear un juego de prueba
            datos_juego = {
                'nombre': 'Juego de Prueba',
                'genero': 'Acción',
                'plataforma': 'PC',
                'desarrollador': 'Test Studio',
                'editor': 'Test Publisher',
                'precio': 29.99,
                'calificacion': 4.5,
                'descripcion': 'Un juego de prueba para verificar el sistema'
            }
            
            nuevo_juego = service.crear(datos_juego)
            if nuevo_juego:
                print(f"✓ Juego creado: {nuevo_juego.nombre}")
                
                # Obtener el juego
                juego_obtenido = service.obtener_por_id(nuevo_juego.id)
                if juego_obtenido:
                    print(f"✓ Juego obtenido: {juego_obtenido.nombre}")
                
                # Obtener todos los juegos
                todos_juegos = service.obtener_todos()
                print(f"✓ Total de juegos: {todos_juegos['total']}")
                
                # Buscar juegos
                resultados = service.buscar_global('Prueba')
                print(f"✓ Búsqueda encontró: {resultados['total']} resultados")
                
                return True
            else:
                print("✗ Error creando juego")
                return False
                
        except Exception as e:
            print(f"✗ Error en servicio de juegos: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_api_manager():
    """Prueba el administrador de APIs"""
    print("\n=== Probando API Manager ===")
    
    try:
        manager = APIManager()
        
        # Probar conexiones
        connections = manager.test_connections()
        print(f"✓ Conexiones: {connections}")
        
        # Buscar juegos
        if connections.get('mock'):
            resultados = manager.buscar_y_sugerir_juegos("Cyberpunk")
            print(f"✓ Sugerencias encontradas: {len(resultados.get('mock', []))}")
            
            for juego in resultados.get('mock', [])[:2]:
                print(f"  - {juego.get('nombre', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error en API Manager: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Iniciando pruebas del backend...\n")
    
    success = True
    
    # Probar base de datos
    if not test_database():
        success = False
    
    # Probar servicio de juegos
    if not test_juegos_service():
        success = False
    
    # Probar API manager
    if not test_api_manager():
        success = False
    
    if success:
        print("\n✓ Todas las pruebas pasaron exitosamente")
    else:
        print("\n✗ Algunas pruebas fallaron")
    
    # Limpiar archivo de prueba
    try:
        os.remove('test_videojuegos.db')
        print("✓ Archivo de prueba limpiado")
    except:
        pass

