"""
Rutas para el catálogo general
"""
from flask import Blueprint, request, jsonify
from src.services.catalogo_service import CatalogoService

catalogo_bp = Blueprint('catalogo', __name__)
catalogo_service = CatalogoService()

@catalogo_bp.route('/buscar', methods=['GET'])
def buscar_global():
    """Búsqueda global en todo el catálogo"""
    try:
        termino = request.args.get('q', '')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        if not termino:
            return jsonify({
                'success': False,
                'error': 'Término de búsqueda requerido'
            }), 400
        
        resultado = catalogo_service.buscar_global(termino, page, per_page)
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@catalogo_bp.route('/destacados', methods=['GET'])
def obtener_destacados():
    """Obtiene productos destacados de cada categoría"""
    try:
        destacados = catalogo_service.obtener_destacados()
        
        return jsonify({
            'success': True,
            'data': destacados
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@catalogo_bp.route('/estadisticas', methods=['GET'])
def obtener_estadisticas_generales():
    """Obtiene estadísticas generales del catálogo"""
    try:
        stats = catalogo_service.obtener_estadisticas_generales()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@catalogo_bp.route('/categoria/<categoria>', methods=['GET'])
def obtener_por_categoria(categoria):
    """Obtiene productos por categoría específica"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        resultado = catalogo_service.obtener_por_categoria(categoria, page, per_page)
        
        return jsonify({
            'success': True,
            'data': resultado,
            'categoria': categoria
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@catalogo_bp.route('/filtros', methods=['GET'])
def obtener_filtros_disponibles():
    """Obtiene todos los filtros disponibles para el catálogo"""
    try:
        filtros = catalogo_service.obtener_filtros_disponibles()
        
        return jsonify({
            'success': True,
            'data': filtros
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@catalogo_bp.route('/', methods=['GET'])
def obtener_resumen_catalogo():
    """Obtiene un resumen general del catálogo"""
    try:
        # Obtener estadísticas generales
        stats = catalogo_service.obtener_estadisticas_generales()
        
        # Obtener productos destacados
        destacados = catalogo_service.obtener_destacados()
        
        # Obtener filtros disponibles
        filtros = catalogo_service.obtener_filtros_disponibles()
        
        return jsonify({
            'success': True,
            'data': {
                'estadisticas': stats,
                'destacados': destacados,
                'filtros_disponibles': filtros
            },
            'message': 'Catálogo de videojuegos - Resumen general'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

