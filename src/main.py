import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models import db, Juego, Consola, Accesorio, HistorialAccion

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'videojuegos_system_secret_key_2024'

# Configuración de CORS para permitir requests desde cualquier origen
CORS(app)

# Configuración de SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///videojuegos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar base de datos
db.init_app(app)

# Crear tablas
with app.app_context():
    db.create_all()
    print("Base de datos inicializada correctamente")

# Registrar blueprints
from src.routes.juegos import juegos_bp

app.register_blueprint(juegos_bp, url_prefix='/api/juegos')

# Rutas que se agregarán en las siguientes fases
# from src.routes.consolas import consolas_bp
# from src.routes.accesorios import accesorios_bp
# from src.routes.catalogo import catalogo_bp
# from src.routes.comparacion import comparacion_bp
# from src.routes.main import main_bp

# app.register_blueprint(main_bp)
# app.register_blueprint(consolas_bp, url_prefix='/api/consolas')
# app.register_blueprint(accesorios_bp, url_prefix='/api/accesorios')
# app.register_blueprint(catalogo_bp, url_prefix='/api/catalogo')
# app.register_blueprint(comparacion_bp, url_prefix='/api/comparacion')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "Sistema de Gestión de Videojuegos - API funcionando correctamente", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
