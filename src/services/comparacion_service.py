"""
Servicio para comparación de productos
"""
from typing import Dict, List, Optional
from src.models import db, Juego, Consola, Accesorio
from src.services.juegos_service import JuegosService
from src.services.consolas_service import ConsolasService
from src.services.accesorios_service import AccesoriosService

class ComparacionService:
    """Servicio para comparación de productos"""
    
    def __init__(self):
        self.juegos_service = JuegosService()
        self.consolas_service = ConsolasService()
        self.accesorios_service = AccesoriosService()
    
    def comparar_juegos(self, ids_juegos: List[int]) -> Dict:
        """Compara múltiples juegos"""
        try:
            if len(ids_juegos) < 2:
                return {
                    'error': 'Se requieren al menos 2 juegos para comparar',
                    'juegos': []
                }
            
            if len(ids_juegos) > 5:
                return {
                    'error': 'Máximo 5 juegos pueden ser comparados a la vez',
                    'juegos': []
                }
            
            juegos = []
            for id_juego in ids_juegos:
                juego = self.juegos_service.obtener_por_id(id_juego)
                if juego:
                    juegos.append(juego.to_dict())
            
            if len(juegos) < 2:
                return {
                    'error': 'No se encontraron suficientes juegos válidos',
                    'juegos': juegos
                }
            
            # Análisis comparativo
            analisis = self._analizar_juegos(juegos)
            
            return {
                'tipo_comparacion': 'juegos',
                'cantidad_comparados': len(juegos),
                'juegos': juegos,
                'analisis': analisis
            }
            
        except Exception as e:
            print(f"Error comparando juegos: {e}")
            return {
                'error': str(e),
                'juegos': []
            }
    
    def comparar_consolas(self, ids_consolas: List[int]) -> Dict:
        """Compara múltiples consolas"""
        try:
            if len(ids_consolas) < 2:
                return {
                    'error': 'Se requieren al menos 2 consolas para comparar',
                    'consolas': []
                }
            
            if len(ids_consolas) > 5:
                return {
                    'error': 'Máximo 5 consolas pueden ser comparadas a la vez',
                    'consolas': []
                }
            
            consolas = []
            for id_consola in ids_consolas:
                consola = self.consolas_service.obtener_por_id(id_consola)
                if consola:
                    consolas.append(consola.to_dict())
            
            if len(consolas) < 2:
                return {
                    'error': 'No se encontraron suficientes consolas válidas',
                    'consolas': consolas
                }
            
            # Análisis comparativo
            analisis = self._analizar_consolas(consolas)
            
            return {
                'tipo_comparacion': 'consolas',
                'cantidad_comparados': len(consolas),
                'consolas': consolas,
                'analisis': analisis
            }
            
        except Exception as e:
            print(f"Error comparando consolas: {e}")
            return {
                'error': str(e),
                'consolas': []
            }
    
    def comparar_accesorios(self, ids_accesorios: List[int]) -> Dict:
        """Compara múltiples accesorios"""
        try:
            if len(ids_accesorios) < 2:
                return {
                    'error': 'Se requieren al menos 2 accesorios para comparar',
                    'accesorios': []
                }
            
            if len(ids_accesorios) > 5:
                return {
                    'error': 'Máximo 5 accesorios pueden ser comparados a la vez',
                    'accesorios': []
                }
            
            accesorios = []
            for id_accesorio in ids_accesorios:
                accesorio = self.accesorios_service.obtener_por_id(id_accesorio)
                if accesorio:
                    accesorios.append(accesorio.to_dict())
            
            if len(accesorios) < 2:
                return {
                    'error': 'No se encontraron suficientes accesorios válidos',
                    'accesorios': accesorios
                }
            
            # Análisis comparativo
            analisis = self._analizar_accesorios(accesorios)
            
            return {
                'tipo_comparacion': 'accesorios',
                'cantidad_comparados': len(accesorios),
                'accesorios': accesorios,
                'analisis': analisis
            }
            
        except Exception as e:
            print(f"Error comparando accesorios: {e}")
            return {
                'error': str(e),
                'accesorios': []
            }
    
    def _analizar_juegos(self, juegos: List[Dict]) -> Dict:
        """Analiza y compara características de juegos"""
        try:
            precios = [j.get('precio', 0) for j in juegos if j.get('precio')]
            calificaciones = [j.get('calificacion', 0) for j in juegos if j.get('calificacion')]
            
            # Análisis de precios
            precio_mas_alto = max(precios) if precios else 0
            precio_mas_bajo = min(precios) if precios else 0
            precio_promedio = sum(precios) / len(precios) if precios else 0
            
            # Análisis de calificaciones
            mejor_calificado = max(calificaciones) if calificaciones else 0
            peor_calificado = min(calificaciones) if calificaciones else 0
            calificacion_promedio = sum(calificaciones) / len(calificaciones) if calificaciones else 0
            
            # Géneros únicos
            generos = set()
            for juego in juegos:
                if juego.get('genero'):
                    generos.update([g.strip() for g in juego['genero'].split(',')])
            
            # Plataformas únicas
            plataformas = set()
            for juego in juegos:
                if juego.get('plataforma'):
                    plataformas.update([p.strip() for p in juego['plataforma'].split(',')])
            
            # Desarrolladores únicos
            desarrolladores = set(j.get('desarrollador', '') for j in juegos if j.get('desarrollador'))
            
            return {
                'precios': {
                    'mas_alto': precio_mas_alto,
                    'mas_bajo': precio_mas_bajo,
                    'promedio': round(precio_promedio, 2),
                    'diferencia': precio_mas_alto - precio_mas_bajo
                },
                'calificaciones': {
                    'mejor': mejor_calificado,
                    'peor': peor_calificado,
                    'promedio': round(calificacion_promedio, 2)
                },
                'diversidad': {
                    'generos_unicos': list(generos),
                    'plataformas_unicas': list(plataformas),
                    'desarrolladores_unicos': list(desarrolladores)
                },
                'recomendacion': self._generar_recomendacion_juegos(juegos, calificaciones, precios)
            }
            
        except Exception as e:
            print(f"Error analizando juegos: {e}")
            return {}
    
    def _analizar_consolas(self, consolas: List[Dict]) -> Dict:
        """Analiza y compara características de consolas"""
        try:
            precios = [c.get('precio', 0) for c in consolas if c.get('precio')]
            generaciones = [c.get('generacion', 0) for c in consolas if c.get('generacion')]
            
            # Análisis de precios
            precio_mas_alto = max(precios) if precios else 0
            precio_mas_bajo = min(precios) if precios else 0
            precio_promedio = sum(precios) / len(precios) if precios else 0
            
            # Análisis de generaciones
            generacion_mas_nueva = max(generaciones) if generaciones else 0
            generacion_mas_antigua = min(generaciones) if generaciones else 0
            
            # Fabricantes únicos
            fabricantes = set(c.get('fabricante', '') for c in consolas if c.get('fabricante'))
            
            # Tipos únicos
            tipos = set(c.get('tipo', '') for c in consolas if c.get('tipo'))
            
            return {
                'precios': {
                    'mas_alto': precio_mas_alto,
                    'mas_bajo': precio_mas_bajo,
                    'promedio': round(precio_promedio, 2),
                    'diferencia': precio_mas_alto - precio_mas_bajo
                },
                'generaciones': {
                    'mas_nueva': generacion_mas_nueva,
                    'mas_antigua': generacion_mas_antigua,
                    'rango': generacion_mas_nueva - generacion_mas_antigua
                },
                'diversidad': {
                    'fabricantes_unicos': list(fabricantes),
                    'tipos_unicos': list(tipos)
                },
                'recomendacion': self._generar_recomendacion_consolas(consolas, generaciones, precios)
            }
            
        except Exception as e:
            print(f"Error analizando consolas: {e}")
            return {}
    
    def _analizar_accesorios(self, accesorios: List[Dict]) -> Dict:
        """Analiza y compara características de accesorios"""
        try:
            precios = [a.get('precio', 0) for a in accesorios if a.get('precio')]
            
            # Análisis de precios
            precio_mas_alto = max(precios) if precios else 0
            precio_mas_bajo = min(precios) if precios else 0
            precio_promedio = sum(precios) / len(precios) if precios else 0
            
            # Tipos únicos
            tipos = set(a.get('tipo', '') for a in accesorios if a.get('tipo'))
            
            # Fabricantes únicos
            fabricantes = set(a.get('fabricante', '') for a in accesorios if a.get('fabricante'))
            
            # Compatibilidades únicas
            compatibilidades = set()
            for accesorio in accesorios:
                if accesorio.get('compatibilidad'):
                    compatibilidades.update([c.strip() for c in accesorio['compatibilidad'].split(',')])
            
            return {
                'precios': {
                    'mas_alto': precio_mas_alto,
                    'mas_bajo': precio_mas_bajo,
                    'promedio': round(precio_promedio, 2),
                    'diferencia': precio_mas_alto - precio_mas_bajo
                },
                'diversidad': {
                    'tipos_unicos': list(tipos),
                    'fabricantes_unicos': list(fabricantes),
                    'compatibilidades_unicas': list(compatibilidades)
                },
                'recomendacion': self._generar_recomendacion_accesorios(accesorios, precios)
            }
            
        except Exception as e:
            print(f"Error analizando accesorios: {e}")
            return {}
    
    def _generar_recomendacion_juegos(self, juegos: List[Dict], calificaciones: List[float], precios: List[float]) -> str:
        """Genera recomendación para juegos"""
        if not juegos:
            return "No hay suficientes datos para generar recomendación"
        
        # Encontrar el mejor juego por calificación
        if calificaciones:
            mejor_calificacion = max(calificaciones)
            mejor_juego = next((j for j in juegos if j.get('calificacion') == mejor_calificacion), None)
            if mejor_juego:
                return f"Recomendado: '{mejor_juego['nombre']}' por su excelente calificación de {mejor_calificacion}"
        
        # Si no hay calificaciones, recomendar por precio
        if precios:
            precio_mas_bajo = min(precios)
            juego_economico = next((j for j in juegos if j.get('precio') == precio_mas_bajo), None)
            if juego_economico:
                return f"Opción económica: '{juego_economico['nombre']}' por ${precio_mas_bajo}"
        
        return f"Todos los juegos comparados ofrecen diferentes ventajas según tus preferencias"
    
    def _generar_recomendacion_consolas(self, consolas: List[Dict], generaciones: List[int], precios: List[float]) -> str:
        """Genera recomendación para consolas"""
        if not consolas:
            return "No hay suficientes datos para generar recomendación"
        
        # Recomendar la consola más nueva
        if generaciones:
            generacion_mas_nueva = max(generaciones)
            consola_nueva = next((c for c in consolas if c.get('generacion') == generacion_mas_nueva), None)
            if consola_nueva:
                return f"Tecnología más avanzada: '{consola_nueva['nombre']}' (Generación {generacion_mas_nueva})"
        
        return "Cada consola tiene sus propias ventajas según el tipo de juegos que prefieras"
    
    def _generar_recomendacion_accesorios(self, accesorios: List[Dict], precios: List[float]) -> str:
        """Genera recomendación para accesorios"""
        if not accesorios:
            return "No hay suficientes datos para generar recomendación"
        
        # Recomendar el más económico
        if precios:
            precio_mas_bajo = min(precios)
            accesorio_economico = next((a for a in accesorios if a.get('precio') == precio_mas_bajo), None)
            if accesorio_economico:
                return f"Mejor relación calidad-precio: '{accesorio_economico['nombre']}' por ${precio_mas_bajo}"
        
        return "Considera la compatibilidad con tus dispositivos al elegir"

