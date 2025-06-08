"""
Rutas para el manejo de consolas
"""
from flask import Blueprint, request, jsonify
from src.services.consolas_service import ConsolasService

consolas_bp = Blueprint('consolas', __name__)
consolas_service = ConsolasService()

@consolas_bp.route('/', methods=['GET'])
def obtener_consolas():
    """Obtiene lista de consolas con paginación y filtros"""
    try:
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Parámetros de filtro
        criterios = {}
        if request.args.get('nombre'):
            criterios['nombre'] = request.args.get('nombre')
        if request.args.get('fabricante'):
            criterios['fabricante'] = request.args.get('fabricante')
        if request.args.get('tipo'):
            criterios['tipo'] = request.args.get('tipo')
        if request.args.get('generacion'):
            criterios['generacion'] = int(request.args.get('generacion'))
        if request.args.get('precio_min'):
            criterios['precio_min'] = float(request.args.get('precio_min'))
        if request.args.get('precio_max'):
            criterios['precio_max'] = float(request.args.get('precio_max'))
        if request.args.get('busqueda'):
            criterios['busqueda_global'] = request.args.get('busqueda')
        
        # Obtener datos
        if criterios:
            resultado = consolas_service.buscar(criterios, page, per_page)
        else:
            resultado = consolas_service.obtener_todos(page, per_page)
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@consolas_bp.route('/<int:id>', methods=['GET'])
def obtener_consola(id):
    """Obtiene una consola específica por ID"""
    try:
        consola = consolas_service.obtener_por_id(id)
        
        if not consola:
            return jsonify({
                'success': False,
                'error': 'Consola no encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'data': consola.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@consolas_bp.route('/', methods=['POST'])
def crear_consola():
    """Crea una nueva consola"""
    try:
        datos = request.get_json()
        
        if not datos:
            return jsonify({
                'success': False,
                'error': 'No se proporcionaron datos'
            }), 400
        
        # Validar campos requeridos
        campos_requeridos = ['nombre', 'fabricante', 'tipo']
        for campo in campos_requeridos:
            if not datos.get(campo):
                return jsonify({
                    'success': False,
                    'error': f'El campo {campo} es requerido'
                }), 400
        
        # Crear consola
        nueva_consola = consolas_service.crear(datos)
        
        if not nueva_consola:
            return jsonify({
                'success': False,
                'error': 'Error al crear la consola'
            }), 500
        
        return jsonify({
            'success': True,
            'data': nueva_consola.to_dict(),
            'message': 'Consola creada exitosamente'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@consolas_bp.route('/<int:id>', methods=['PUT'])
def actualizar_consola(id):
    """Actualiza una consola existente"""
    try:
        datos = request.get_json()
        
        if not datos:
            return jsonify({
                'success': False,
                'error': 'No se proporcionaron datos'
            }), 400
        
        # Actualizar consola
        consola_actualizada = consolas_service.actualizar(id, datos)
        
        if not consola_actualizada:
            return jsonify({
                'success': False,
                'error': 'Consola no encontrada o error al actualizar'
            }), 404
        
        return jsonify({
            'success': True,
            'data': consola_actualizada.to_dict(),
            'message': 'Consola actualizada exitosamente'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@consolas_bp.route('/<int:id>', methods=['DELETE'])
def eliminar_consola(id):
    """Elimina una consola (soft delete)"""
    try:
        eliminado = consolas_service.eliminar(id)
        
        if not eliminado:
            return jsonify({
                'success': False,
                'error': 'Consola no encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Consola eliminada exitosamente'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@consolas_bp.route('/buscar', methods=['GET'])
def buscar_consolas():
    """Búsqueda avanzada de consolas"""
    try:
        termino = request.args.get('q', '')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        if not termino:
            return jsonify({
                'success': False,
                'error': 'Término de búsqueda requerido'
            }), 400
        
        resultado = consolas_service.buscar_global(termino, page, per_page)
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@consolas_bp.route('/fabricantes/<fabricante>', methods=['GET'])
def obtener_por_fabricante(fabricante):
    """Obtiene consolas por fabricante"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        resultado = consolas_service.obtener_por_fabricante(fabricante, page, per_page)
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@consolas_bp.route('/tipos/<tipo>', methods=['GET'])
def obtener_por_tipo(tipo):
    """Obtiene consolas por tipo"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        resultado = consolas_service.obtener_por_tipo(tipo, page, per_page)
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@consolas_bp.route('/generaciones/<int:generacion>', methods=['GET'])
def obtener_por_generacion(generacion):
    """Obtiene consolas por generación"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        resultado = consolas_service.obtener_por_generacion(generacion, page, per_page)
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@consolas_bp.route('/recientes', methods=['GET'])
def obtener_consolas_recientes():
    """Obtiene las consolas más recientes"""
    try:
        limit = min(request.args.get('limit', 10, type=int), 50)
        
        consolas = consolas_service.obtener_mas_recientes(limit)
        
        return jsonify({
            'success': True,
            'data': consolas
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@consolas_bp.route('/estadisticas', methods=['GET'])
def obtener_estadisticas():
    """Obtiene estadísticas de las consolas"""
    try:
        stats = consolas_service.obtener_estadisticas()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

