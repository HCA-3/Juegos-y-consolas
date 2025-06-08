"""
Rutas para comparación de productos
"""
from flask import Blueprint, request, jsonify
from src.services.comparacion_service import ComparacionService

comparacion_bp = Blueprint('comparacion', __name__)
comparacion_service = ComparacionService()

@comparacion_bp.route('/juegos', methods=['POST'])
def comparar_juegos():
    """Compara múltiples juegos"""
    try:
        datos = request.get_json()
        
        if not datos or 'ids' not in datos:
            return jsonify({
                'success': False,
                'error': 'Se requiere una lista de IDs de juegos'
            }), 400
        
        ids_juegos = datos['ids']
        
        if not isinstance(ids_juegos, list):
            return jsonify({
                'success': False,
                'error': 'Los IDs deben ser una lista'
            }), 400
        
        resultado = comparacion_service.comparar_juegos(ids_juegos)
        
        if 'error' in resultado:
            return jsonify({
                'success': False,
                'error': resultado['error'],
                'data': resultado
            }), 400
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@comparacion_bp.route('/consolas', methods=['POST'])
def comparar_consolas():
    """Compara múltiples consolas"""
    try:
        datos = request.get_json()
        
        if not datos or 'ids' not in datos:
            return jsonify({
                'success': False,
                'error': 'Se requiere una lista de IDs de consolas'
            }), 400
        
        ids_consolas = datos['ids']
        
        if not isinstance(ids_consolas, list):
            return jsonify({
                'success': False,
                'error': 'Los IDs deben ser una lista'
            }), 400
        
        resultado = comparacion_service.comparar_consolas(ids_consolas)
        
        if 'error' in resultado:
            return jsonify({
                'success': False,
                'error': resultado['error'],
                'data': resultado
            }), 400
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@comparacion_bp.route('/accesorios', methods=['POST'])
def comparar_accesorios():
    """Compara múltiples accesorios"""
    try:
        datos = request.get_json()
        
        if not datos or 'ids' not in datos:
            return jsonify({
                'success': False,
                'error': 'Se requiere una lista de IDs de accesorios'
            }), 400
        
        ids_accesorios = datos['ids']
        
        if not isinstance(ids_accesorios, list):
            return jsonify({
                'success': False,
                'error': 'Los IDs deben ser una lista'
            }), 400
        
        resultado = comparacion_service.comparar_accesorios(ids_accesorios)
        
        if 'error' in resultado:
            return jsonify({
                'success': False,
                'error': resultado['error'],
                'data': resultado
            }), 400
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@comparacion_bp.route('/juegos', methods=['GET'])
def comparar_juegos_get():
    """Compara juegos usando parámetros GET"""
    try:
        ids_str = request.args.get('ids', '')
        
        if not ids_str:
            return jsonify({
                'success': False,
                'error': 'Se requieren IDs de juegos (parámetro ids)'
            }), 400
        
        try:
            ids_juegos = [int(id.strip()) for id in ids_str.split(',') if id.strip()]
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Los IDs deben ser números válidos separados por comas'
            }), 400
        
        resultado = comparacion_service.comparar_juegos(ids_juegos)
        
        if 'error' in resultado:
            return jsonify({
                'success': False,
                'error': resultado['error'],
                'data': resultado
            }), 400
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@comparacion_bp.route('/consolas', methods=['GET'])
def comparar_consolas_get():
    """Compara consolas usando parámetros GET"""
    try:
        ids_str = request.args.get('ids', '')
        
        if not ids_str:
            return jsonify({
                'success': False,
                'error': 'Se requieren IDs de consolas (parámetro ids)'
            }), 400
        
        try:
            ids_consolas = [int(id.strip()) for id in ids_str.split(',') if id.strip()]
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Los IDs deben ser números válidos separados por comas'
            }), 400
        
        resultado = comparacion_service.comparar_consolas(ids_consolas)
        
        if 'error' in resultado:
            return jsonify({
                'success': False,
                'error': resultado['error'],
                'data': resultado
            }), 400
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@comparacion_bp.route('/accesorios', methods=['GET'])
def comparar_accesorios_get():
    """Compara accesorios usando parámetros GET"""
    try:
        ids_str = request.args.get('ids', '')
        
        if not ids_str:
            return jsonify({
                'success': False,
                'error': 'Se requieren IDs de accesorios (parámetro ids)'
            }), 400
        
        try:
            ids_accesorios = [int(id.strip()) for id in ids_str.split(',') if id.strip()]
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Los IDs deben ser números válidos separados por comas'
            }), 400
        
        resultado = comparacion_service.comparar_accesorios(ids_accesorios)
        
        if 'error' in resultado:
            return jsonify({
                'success': False,
                'error': resultado['error'],
                'data': resultado
            }), 400
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@comparacion_bp.route('/', methods=['GET'])
def obtener_info_comparacion():
    """Obtiene información sobre las funcionalidades de comparación"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'message': 'Servicio de comparación de productos',
                'endpoints': {
                    'comparar_juegos': {
                        'POST': '/comparacion/juegos',
                        'GET': '/comparacion/juegos?ids=1,2,3',
                        'descripcion': 'Compara hasta 5 juegos'
                    },
                    'comparar_consolas': {
                        'POST': '/comparacion/consolas',
                        'GET': '/comparacion/consolas?ids=1,2,3',
                        'descripcion': 'Compara hasta 5 consolas'
                    },
                    'comparar_accesorios': {
                        'POST': '/comparacion/accesorios',
                        'GET': '/comparacion/accesorios?ids=1,2,3',
                        'descripcion': 'Compara hasta 5 accesorios'
                    }
                },
                'formato_post': {
                    'ejemplo': {
                        'ids': [1, 2, 3]
                    }
                },
                'limitaciones': {
                    'minimo_productos': 2,
                    'maximo_productos': 5
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

