"""
Rutas para el manejo de juegos
"""
from flask import Blueprint, request, jsonify
from src.services.juegos_service import JuegosService
from src.api.api_manager import APIManager

juegos_bp = Blueprint('juegos', __name__)
juegos_service = JuegosService()
api_manager = APIManager()

@juegos_bp.route('/', methods=['GET'])
def obtener_juegos():
    """Obtiene lista de juegos con paginación y filtros"""
    try:
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)  # Máximo 100
        
        # Parámetros de filtro
        criterios = {}
        if request.args.get('nombre'):
            criterios['nombre'] = request.args.get('nombre')
        if request.args.get('genero'):
            criterios['genero'] = request.args.get('genero')
        if request.args.get('plataforma'):
            criterios['plataforma'] = request.args.get('plataforma')
        if request.args.get('desarrollador'):
            criterios['desarrollador'] = request.args.get('desarrollador')
        if request.args.get('precio_min'):
            criterios['precio_min'] = float(request.args.get('precio_min'))
        if request.args.get('precio_max'):
            criterios['precio_max'] = float(request.args.get('precio_max'))
        if request.args.get('busqueda'):
            criterios['busqueda_global'] = request.args.get('busqueda')
        
        # Obtener datos
        if criterios:
            resultado = juegos_service.buscar(criterios, page, per_page)
        else:
            resultado = juegos_service.obtener_todos(page, per_page)
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@juegos_bp.route('/<int:id>', methods=['GET'])
def obtener_juego(id):
    """Obtiene un juego específico por ID"""
    try:
        juego = juegos_service.obtener_por_id(id)
        
        if not juego:
            return jsonify({
                'success': False,
                'error': 'Juego no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': juego.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@juegos_bp.route('/', methods=['POST'])
def crear_juego():
    """Crea un nuevo juego"""
    try:
        datos = request.get_json()
        
        if not datos:
            return jsonify({
                'success': False,
                'error': 'No se proporcionaron datos'
            }), 400
        
        # Validar campos requeridos
        campos_requeridos = ['nombre', 'genero', 'plataforma', 'desarrollador']
        for campo in campos_requeridos:
            if not datos.get(campo):
                return jsonify({
                    'success': False,
                    'error': f'El campo {campo} es requerido'
                }), 400
        
        # Crear juego
        nuevo_juego = juegos_service.crear(datos)
        
        if not nuevo_juego:
            return jsonify({
                'success': False,
                'error': 'Error al crear el juego'
            }), 500
        
        return jsonify({
            'success': True,
            'data': nuevo_juego.to_dict(),
            'message': 'Juego creado exitosamente'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@juegos_bp.route('/<int:id>', methods=['PUT'])
def actualizar_juego(id):
    """Actualiza un juego existente"""
    try:
        datos = request.get_json()
        
        if not datos:
            return jsonify({
                'success': False,
                'error': 'No se proporcionaron datos'
            }), 400
        
        # Actualizar juego
        juego_actualizado = juegos_service.actualizar(id, datos)
        
        if not juego_actualizado:
            return jsonify({
                'success': False,
                'error': 'Juego no encontrado o error al actualizar'
            }), 404
        
        return jsonify({
            'success': True,
            'data': juego_actualizado.to_dict(),
            'message': 'Juego actualizado exitosamente'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@juegos_bp.route('/<int:id>', methods=['DELETE'])
def eliminar_juego(id):
    """Elimina un juego (soft delete)"""
    try:
        eliminado = juegos_service.eliminar(id)
        
        if not eliminado:
            return jsonify({
                'success': False,
                'error': 'Juego no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Juego eliminado exitosamente'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@juegos_bp.route('/buscar', methods=['GET'])
def buscar_juegos():
    """Búsqueda avanzada de juegos"""
    try:
        termino = request.args.get('q', '')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        if not termino:
            return jsonify({
                'success': False,
                'error': 'Término de búsqueda requerido'
            }), 400
        
        resultado = juegos_service.buscar_global(termino, page, per_page)
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@juegos_bp.route('/populares', methods=['GET'])
def obtener_juegos_populares():
    """Obtiene los juegos más populares"""
    try:
        limit = min(request.args.get('limit', 10, type=int), 50)
        
        juegos = juegos_service.obtener_mejor_calificados(limit)
        
        return jsonify({
            'success': True,
            'data': juegos
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@juegos_bp.route('/recientes', methods=['GET'])
def obtener_juegos_recientes():
    """Obtiene los juegos más recientes"""
    try:
        limit = min(request.args.get('limit', 10, type=int), 50)
        
        juegos = juegos_service.obtener_mas_recientes(limit)
        
        return jsonify({
            'success': True,
            'data': juegos
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@juegos_bp.route('/estadisticas', methods=['GET'])
def obtener_estadisticas():
    """Obtiene estadísticas de los juegos"""
    try:
        stats = juegos_service.obtener_estadisticas()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@juegos_bp.route('/sync/populares', methods=['POST'])
def sincronizar_juegos_populares():
    """Sincroniza juegos populares desde APIs externas"""
    try:
        limit = min(request.json.get('limit', 5) if request.json else 5, 10)
        
        juegos_sincronizados = api_manager.sincronizar_juegos_populares(limit=limit)
        
        return jsonify({
            'success': True,
            'data': [juego.to_dict() for juego in juegos_sincronizados],
            'message': f'{len(juegos_sincronizados)} juegos sincronizados'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@juegos_bp.route('/sugerencias', methods=['GET'])
def obtener_sugerencias():
    """Obtiene sugerencias de juegos desde APIs externas"""
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Término de búsqueda requerido'
            }), 400
        
        sugerencias = api_manager.buscar_y_sugerir_juegos(query)
        
        return jsonify({
            'success': True,
            'data': sugerencias
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

