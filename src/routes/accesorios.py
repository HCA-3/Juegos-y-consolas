"""
Rutas para el manejo de accesorios
"""
from flask import Blueprint, request, jsonify
from src.services.accesorios_service import AccesoriosService

accesorios_bp = Blueprint('accesorios', __name__)
accesorios_service = AccesoriosService()

@accesorios_bp.route('/', methods=['GET'])
def obtener_accesorios():
    """Obtiene lista de accesorios con paginación y filtros"""
    try:
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Parámetros de filtro
        criterios = {}
        if request.args.get('nombre'):
            criterios['nombre'] = request.args.get('nombre')
        if request.args.get('tipo'):
            criterios['tipo'] = request.args.get('tipo')
        if request.args.get('fabricante'):
            criterios['fabricante'] = request.args.get('fabricante')
        if request.args.get('compatibilidad'):
            criterios['compatibilidad'] = request.args.get('compatibilidad')
        if request.args.get('precio_min'):
            criterios['precio_min'] = float(request.args.get('precio_min'))
        if request.args.get('precio_max'):
            criterios['precio_max'] = float(request.args.get('precio_max'))
        if request.args.get('busqueda'):
            criterios['busqueda_global'] = request.args.get('busqueda')
        
        # Obtener datos
        if criterios:
            resultado = accesorios_service.buscar(criterios, page, per_page)
        else:
            resultado = accesorios_service.obtener_todos(page, per_page)
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@accesorios_bp.route('/<int:id>', methods=['GET'])
def obtener_accesorio(id):
    """Obtiene un accesorio específico por ID"""
    try:
        accesorio = accesorios_service.obtener_por_id(id)
        
        if not accesorio:
            return jsonify({
                'success': False,
                'error': 'Accesorio no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': accesorio.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@accesorios_bp.route('/', methods=['POST'])
def crear_accesorio():
    """Crea un nuevo accesorio"""
    try:
        datos = request.get_json()
        
        if not datos:
            return jsonify({
                'success': False,
                'error': 'No se proporcionaron datos'
            }), 400
        
        # Validar campos requeridos
        campos_requeridos = ['nombre', 'tipo', 'fabricante']
        for campo in campos_requeridos:
            if not datos.get(campo):
                return jsonify({
                    'success': False,
                    'error': f'El campo {campo} es requerido'
                }), 400
        
        # Crear accesorio
        nuevo_accesorio = accesorios_service.crear(datos)
        
        if not nuevo_accesorio:
            return jsonify({
                'success': False,
                'error': 'Error al crear el accesorio'
            }), 500
        
        return jsonify({
            'success': True,
            'data': nuevo_accesorio.to_dict(),
            'message': 'Accesorio creado exitosamente'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@accesorios_bp.route('/<int:id>', methods=['PUT'])
def actualizar_accesorio(id):
    """Actualiza un accesorio existente"""
    try:
        datos = request.get_json()
        
        if not datos:
            return jsonify({
                'success': False,
                'error': 'No se proporcionaron datos'
            }), 400
        
        # Actualizar accesorio
        accesorio_actualizado = accesorios_service.actualizar(id, datos)
        
        if not accesorio_actualizado:
            return jsonify({
                'success': False,
                'error': 'Accesorio no encontrado o error al actualizar'
            }), 404
        
        return jsonify({
            'success': True,
            'data': accesorio_actualizado.to_dict(),
            'message': 'Accesorio actualizado exitosamente'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@accesorios_bp.route('/<int:id>', methods=['DELETE'])
def eliminar_accesorio(id):
    """Elimina un accesorio (soft delete)"""
    try:
        eliminado = accesorios_service.eliminar(id)
        
        if not eliminado:
            return jsonify({
                'success': False,
                'error': 'Accesorio no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Accesorio eliminado exitosamente'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@accesorios_bp.route('/buscar', methods=['GET'])
def buscar_accesorios():
    """Búsqueda avanzada de accesorios"""
    try:
        termino = request.args.get('q', '')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        if not termino:
            return jsonify({
                'success': False,
                'error': 'Término de búsqueda requerido'
            }), 400
        
        resultado = accesorios_service.buscar_global(termino, page, per_page)
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@accesorios_bp.route('/tipos/<tipo>', methods=['GET'])
def obtener_por_tipo(tipo):
    """Obtiene accesorios por tipo"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        resultado = accesorios_service.obtener_por_tipo(tipo, page, per_page)
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@accesorios_bp.route('/fabricantes/<fabricante>', methods=['GET'])
def obtener_por_fabricante(fabricante):
    """Obtiene accesorios por fabricante"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        resultado = accesorios_service.obtener_por_fabricante(fabricante, page, per_page)
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@accesorios_bp.route('/compatibilidad/<compatibilidad>', methods=['GET'])
def obtener_por_compatibilidad(compatibilidad):
    """Obtiene accesorios por compatibilidad"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        resultado = accesorios_service.obtener_por_compatibilidad(compatibilidad, page, per_page)
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@accesorios_bp.route('/recientes', methods=['GET'])
def obtener_accesorios_recientes():
    """Obtiene los accesorios más recientes"""
    try:
        limit = min(request.args.get('limit', 10, type=int), 50)
        
        accesorios = accesorios_service.obtener_mas_recientes(limit)
        
        return jsonify({
            'success': True,
            'data': accesorios
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@accesorios_bp.route('/estadisticas', methods=['GET'])
def obtener_estadisticas():
    """Obtiene estadísticas de los accesorios"""
    try:
        stats = accesorios_service.obtener_estadisticas()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

