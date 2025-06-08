"""
Servidor completo para probar todos los endpoints y la interfaz web
"""
from flask import Flask
from flask_cors import CORS
from src.models import db
from src.routes.juegos import juegos_bp
from src.routes.consolas import consolas_bp
from src.routes.accesorios import accesorios_bp
from src.routes.catalogo import catalogo_bp
from src.routes.comparacion import comparacion_bp
from src.routes.web import web_bp

# Crear aplicación Flask
app = Flask(__name__)
CORS(app)

# Configuración
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///videojuegos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'gamehub-secret-key-2025'

# Inicializar base de datos
db.init_app(app)

# Crear tablas
with app.app_context():
    db.create_all()
    print("Base de datos inicializada correctamente")

# Registrar blueprints de API
app.register_blueprint(juegos_bp, url_prefix='/api/juegos')
app.register_blueprint(consolas_bp, url_prefix='/api/consolas')
app.register_blueprint(accesorios_bp, url_prefix='/api/accesorios')
app.register_blueprint(catalogo_bp, url_prefix='/api/catalogo')
app.register_blueprint(comparacion_bp, url_prefix='/api/comparacion')

# Registrar blueprint de páginas web
app.register_blueprint(web_bp)

@app.route('/health')
def health():
    return {'status': 'ok', 'message': 'Sistema funcionando correctamente'}

@app.route('/api')
def api_info():
    return {
        'message': 'API de Sistema de Gestión de Videojuegos',
        'version': '1.0.0',
        'documentacion': 'Consulta los endpoints disponibles en /',
        'funcionalidades': [
            'CRUD completo para Juegos, Consolas y Accesorios',
            'Búsquedas avanzadas y filtros',
            'Catálogo unificado',
            'Comparación de productos',
            'Estadísticas y análisis',
            'Integración con APIs externas',
            'Historial de acciones',
            'Interfaz web interactiva'
        ],
        'endpoints': {
            'web': {
                'dashboard': '/',
                'juegos': '/juegos',
                'consolas': '/consolas',
                'accesorios': '/accesorios',
                'catalogo': '/catalogo',
                'comparacion': '/comparacion',
                'busqueda': '/buscar?q=termino'
            },
            'api': {
                'juegos': '/api/juegos/',
                'consolas': '/api/consolas/',
                'accesorios': '/api/accesorios/',
                'catalogo': '/api/catalogo/',
                'comparacion': '/api/comparacion/'
            }
        }
    }

if __name__ == '__main__':
    print("Iniciando GameHub - Sistema Completo...")
    print("\n=== INTERFAZ WEB ===")
    print("- Dashboard: http://localhost:5002/")
    print("- Juegos: http://localhost:5002/juegos")
    print("- Consolas: http://localhost:5002/consolas")
    print("- Accesorios: http://localhost:5002/accesorios")
    print("- Catálogo: http://localhost:5002/catalogo")
    print("- Comparación: http://localhost:5002/comparacion")
    print("- Búsqueda: http://localhost:5002/buscar")
    
    print("\n=== API ENDPOINTS ===")
    print("=== JUEGOS ===")
    print("- GET/POST /api/juegos/")
    print("- GET/PUT/DELETE /api/juegos/<id>")
    print("- GET /api/juegos/buscar?q=termino")
    print("- GET /api/juegos/populares")
    print("- GET /api/juegos/recientes")
    print("- GET /api/juegos/estadisticas")
    print("- GET /api/juegos/sugerencias?q=termino")
    print("\n=== CONSOLAS ===")
    print("- GET/POST /api/consolas/")
    print("- GET/PUT/DELETE /api/consolas/<id>")
    print("- GET /api/consolas/buscar?q=termino")
    print("- GET /api/consolas/fabricantes/<fabricante>")
    print("- GET /api/consolas/tipos/<tipo>")
    print("- GET /api/consolas/generaciones/<generacion>")
    print("- GET /api/consolas/recientes")
    print("- GET /api/consolas/estadisticas")
    print("\n=== ACCESORIOS ===")
    print("- GET/POST /api/accesorios/")
    print("- GET/PUT/DELETE /api/accesorios/<id>")
    print("- GET /api/accesorios/buscar?q=termino")
    print("- GET /api/accesorios/tipos/<tipo>")
    print("- GET /api/accesorios/fabricantes/<fabricante>")
    print("- GET /api/accesorios/compatibilidad/<compatibilidad>")
    print("- GET /api/accesorios/recientes")
    print("- GET /api/accesorios/estadisticas")
    print("\n=== CATÁLOGO ===")
    print("- GET /api/catalogo/")
    print("- GET /api/catalogo/buscar?q=termino")
    print("- GET /api/catalogo/destacados")
    print("- GET /api/catalogo/estadisticas")
    print("- GET /api/catalogo/categoria/<categoria>")
    print("- GET /api/catalogo/filtros")
    print("\n=== COMPARACIÓN ===")
    print("- GET /api/comparacion/")
    print("- GET/POST /api/comparacion/juegos")
    print("- GET/POST /api/comparacion/consolas")
    print("- GET/POST /api/comparacion/accesorios")
    print("\n🎮 GameHub ejecutándose en http://localhost:5002")
    print("📱 Interfaz responsive y optimizada para móviles")
    print("🚀 API REST completa disponible")
    
    app.run(host='0.0.0.0', port=5002, debug=True)

