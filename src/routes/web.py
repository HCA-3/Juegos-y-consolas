"""
Rutas web para las páginas HTML del sistema
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.services.juegos_service import JuegosService
from src.services.consolas_service import ConsolasService
from src.services.accesorios_service import AccesoriosService
from src.services.catalogo_service import CatalogoService
from src.services.comparacion_service import ComparacionService

# Crear blueprint para rutas web
web_bp = Blueprint('web', __name__)

# Inicializar servicios
juegos_service = JuegosService()
consolas_service = ConsolasService()
accesorios_service = AccesoriosService()
catalogo_service = CatalogoService()
comparacion_service = ComparacionService()

@web_bp.route('/')
def index():
    """Página principal del dashboard"""
    return render_template('index.html')

@web_bp.route('/juegos')
def juegos_lista():
    """Lista de juegos"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    busqueda = request.args.get('q', '')
    
    return render_template('juegos/lista.html', 
                         page=page, 
                         per_page=per_page, 
                         busqueda=busqueda)

@web_bp.route('/juegos/crear')
def juegos_crear():
    """Formulario para crear juego"""
    return render_template('juegos/crear.html')

@web_bp.route('/juegos/<int:id>')
def juegos_detalle(id):
    """Detalle de un juego"""
    return render_template('juegos/detalle.html', juego_id=id)

@web_bp.route('/juegos/<int:id>/editar')
def juegos_editar(id):
    """Formulario para editar juego"""
    return render_template('juegos/editar.html', juego_id=id)

@web_bp.route('/juegos/populares')
def juegos_populares():
    """Juegos populares"""
    return render_template('juegos/populares.html')

@web_bp.route('/juegos/recientes')
def juegos_recientes():
    """Juegos recientes"""
    return render_template('juegos/recientes.html')

@web_bp.route('/consolas')
def consolas_lista():
    """Lista de consolas"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    busqueda = request.args.get('q', '')
    
    return render_template('consolas/lista.html', 
                         page=page, 
                         per_page=per_page, 
                         busqueda=busqueda)

@web_bp.route('/consolas/crear')
def consolas_crear():
    """Formulario para crear consola"""
    return render_template('consolas/crear.html')

@web_bp.route('/consolas/<int:id>')
def consolas_detalle(id):
    """Detalle de una consola"""
    return render_template('consolas/detalle.html', consola_id=id)

@web_bp.route('/consolas/<int:id>/editar')
def consolas_editar(id):
    """Formulario para editar consola"""
    return render_template('consolas/editar.html', consola_id=id)

@web_bp.route('/consolas/fabricantes')
def consolas_fabricantes():
    """Consolas por fabricante"""
    return render_template('consolas/fabricantes.html')

@web_bp.route('/consolas/generaciones')
def consolas_generaciones():
    """Consolas por generación"""
    return render_template('consolas/generaciones.html')

@web_bp.route('/accesorios')
def accesorios_lista():
    """Lista de accesorios"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    busqueda = request.args.get('q', '')
    
    return render_template('accesorios/lista.html', 
                         page=page, 
                         per_page=per_page, 
                         busqueda=busqueda)

@web_bp.route('/accesorios/crear')
def accesorios_crear():
    """Formulario para crear accesorio"""
    return render_template('accesorios/crear.html')

@web_bp.route('/accesorios/<int:id>')
def accesorios_detalle(id):
    """Detalle de un accesorio"""
    return render_template('accesorios/detalle.html', accesorio_id=id)

@web_bp.route('/accesorios/<int:id>/editar')
def accesorios_editar(id):
    """Formulario para editar accesorio"""
    return render_template('accesorios/editar.html', accesorio_id=id)

@web_bp.route('/accesorios/tipos')
def accesorios_tipos():
    """Accesorios por tipo"""
    return render_template('accesorios/tipos.html')

@web_bp.route('/accesorios/compatibilidad')
def accesorios_compatibilidad():
    """Accesorios por compatibilidad"""
    return render_template('accesorios/compatibilidad.html')

@web_bp.route('/catalogo')
def catalogo():
    """Catálogo general"""
    return render_template('catalogo/index.html')

@web_bp.route('/catalogo/buscar')
def catalogo_buscar():
    """Búsqueda en catálogo"""
    termino = request.args.get('q', '')
    categoria = request.args.get('categoria', '')
    page = request.args.get('page', 1, type=int)
    
    return render_template('catalogo/buscar.html', 
                         termino=termino, 
                         categoria=categoria, 
                         page=page)

@web_bp.route('/catalogo/categoria/<categoria>')
def catalogo_categoria(categoria):
    """Productos por categoría"""
    page = request.args.get('page', 1, type=int)
    
    return render_template('catalogo/categoria.html', 
                         categoria=categoria, 
                         page=page)

@web_bp.route('/comparacion')
def comparacion():
    """Página de comparación"""
    return render_template('comparacion/index.html')

@web_bp.route('/comparacion/juegos')
def comparacion_juegos():
    """Comparación de juegos"""
    ids = request.args.get('ids', '')
    return render_template('comparacion/juegos.html', ids=ids)

@web_bp.route('/comparacion/consolas')
def comparacion_consolas():
    """Comparación de consolas"""
    ids = request.args.get('ids', '')
    return render_template('comparacion/consolas.html', ids=ids)

@web_bp.route('/comparacion/accesorios')
def comparacion_accesorios():
    """Comparación de accesorios"""
    ids = request.args.get('ids', '')
    return render_template('comparacion/accesorios.html', ids=ids)

@web_bp.route('/estadisticas')
def estadisticas():
    """Página de estadísticas"""
    return render_template('estadisticas/index.html')

@web_bp.route('/historial')
def historial():
    """Historial de acciones"""
    page = request.args.get('page', 1, type=int)
    return render_template('historial/index.html', page=page)

@web_bp.route('/buscar')
def buscar_global():
    """Búsqueda global"""
    termino = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    return render_template('buscar.html', termino=termino, page=page)

@web_bp.route('/api')
def api_docs():
    """Documentación de la API"""
    return render_template('api/docs.html')

@web_bp.route('/ayuda')
def ayuda():
    """Página de ayuda"""
    return render_template('ayuda.html')

@web_bp.route('/contacto')
def contacto():
    """Página de contacto"""
    return render_template('contacto.html')

@web_bp.route('/about')
def about():
    """Acerca del sistema"""
    return render_template('about.html')

@web_bp.route('/documentacion')
def documentacion():
    """Documentación del sistema"""
    return render_template('documentacion.html')

# Manejadores de errores
@web_bp.errorhandler(404)
def not_found(error):
    """Página 404"""
    return render_template('errors/404.html'), 404

@web_bp.errorhandler(500)
def internal_error(error):
    """Página 500"""
    return render_template('errors/500.html'), 500

# Filtros de template personalizados
@web_bp.app_template_filter('format_price')
def format_price(price):
    """Formatear precio"""
    if price is None:
        return 'N/A'
    return f'${price:,.2f}'

@web_bp.app_template_filter('format_date')
def format_date(date):
    """Formatear fecha"""
    if date is None:
        return 'N/A'
    return date.strftime('%d/%m/%Y')

@web_bp.app_template_filter('truncate_text')
def truncate_text(text, length=100):
    """Truncar texto"""
    if not text:
        return ''
    if len(text) <= length:
        return text
    return text[:length] + '...'

@web_bp.app_template_filter('format_rating')
def format_rating(rating):
    """Formatear calificación"""
    if not rating:
        return 'N/A'
    stars = '★' * int(rating) + '☆' * (5 - int(rating))
    return f'{stars} ({rating}/5)'

