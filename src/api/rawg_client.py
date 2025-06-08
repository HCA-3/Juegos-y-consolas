"""
Cliente para RAWG Video Games Database API
"""
import requests
import time
from typing import Dict, List, Optional

class RAWGClient:
    """Cliente para interactuar con RAWG API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://api.rawg.io/api"
        self.api_key = api_key or "demo"  # Usar demo key si no se proporciona una
        self.session = requests.Session()
        self.last_request_time = 0
        self.rate_limit_delay = 1.0  # 1 segundo entre requests para evitar rate limiting
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Realiza una petición HTTP con rate limiting"""
        # Rate limiting
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last_request)
        
        # Preparar parámetros
        if params is None:
            params = {}
        params['key'] = self.api_key
        
        # Realizar petición
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            self.last_request_time = time.time()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error en petición a RAWG API: {e}")
            return {}
    
    def buscar_juegos(self, query: str, page: int = 1, page_size: int = 20) -> Dict:
        """Busca juegos por nombre"""
        params = {
            'search': query,
            'page': page,
            'page_size': page_size
        }
        return self._make_request('games', params)
    
    def obtener_juego_por_id(self, game_id: int) -> Dict:
        """Obtiene detalles de un juego específico"""
        return self._make_request(f'games/{game_id}')
    
    def obtener_juegos_populares(self, page: int = 1, page_size: int = 20) -> Dict:
        """Obtiene juegos populares ordenados por rating"""
        params = {
            'ordering': '-rating',
            'page': page,
            'page_size': page_size
        }
        return self._make_request('games', params)
    
    def obtener_juegos_por_genero(self, genero: str, page: int = 1, page_size: int = 20) -> Dict:
        """Obtiene juegos filtrados por género"""
        params = {
            'genres': genero,
            'page': page,
            'page_size': page_size
        }
        return self._make_request('games', params)
    
    def obtener_juegos_por_plataforma(self, plataforma: str, page: int = 1, page_size: int = 20) -> Dict:
        """Obtiene juegos filtrados por plataforma"""
        params = {
            'platforms': plataforma,
            'page': page,
            'page_size': page_size
        }
        return self._make_request('games', params)
    
    def obtener_juegos_recientes(self, page: int = 1, page_size: int = 20) -> Dict:
        """Obtiene juegos lanzados recientemente"""
        params = {
            'ordering': '-released',
            'page': page,
            'page_size': page_size
        }
        return self._make_request('games', params)
    
    def obtener_plataformas(self, page: int = 1, page_size: int = 20) -> Dict:
        """Obtiene lista de plataformas"""
        params = {
            'page': page,
            'page_size': page_size
        }
        return self._make_request('platforms', params)
    
    def obtener_generos(self, page: int = 1, page_size: int = 20) -> Dict:
        """Obtiene lista de géneros"""
        params = {
            'page': page,
            'page_size': page_size
        }
        return self._make_request('genres', params)
    
    def obtener_desarrolladores(self, page: int = 1, page_size: int = 20) -> Dict:
        """Obtiene lista de desarrolladores"""
        params = {
            'page': page,
            'page_size': page_size
        }
        return self._make_request('developers', params)
    
    def convertir_a_modelo_juego(self, rawg_game: Dict) -> Dict:
        """Convierte un juego de RAWG al formato de nuestro modelo"""
        try:
            # Extraer plataformas
            plataformas = []
            if rawg_game.get('platforms'):
                plataformas = [p['platform']['name'] for p in rawg_game['platforms']]
            
            # Extraer géneros
            generos = []
            if rawg_game.get('genres'):
                generos = [g['name'] for g in rawg_game['genres']]
            
            # Extraer desarrolladores
            desarrolladores = []
            if rawg_game.get('developers'):
                desarrolladores = [d['name'] for d in rawg_game['developers']]
            
            # Extraer editores
            editores = []
            if rawg_game.get('publishers'):
                editores = [p['name'] for p in rawg_game['publishers']]
            
            return {
                'nombre': rawg_game.get('name', ''),
                'genero': ', '.join(generos) if generos else 'No especificado',
                'plataforma': ', '.join(plataformas) if plataformas else 'No especificado',
                'desarrollador': ', '.join(desarrolladores) if desarrolladores else 'No especificado',
                'editor': ', '.join(editores) if editores else 'No especificado',
                'fecha_lanzamiento': rawg_game.get('released'),
                'precio': None,  # RAWG no proporciona precios
                'calificacion': rawg_game.get('rating'),
                'descripcion': rawg_game.get('description_raw', ''),
                'imagen_url': rawg_game.get('background_image', ''),
                'api_id': str(rawg_game.get('id', ''))
            }
        except Exception as e:
            print(f"Error convirtiendo juego de RAWG: {e}")
            return {}
    
    def test_connection(self) -> bool:
        """Prueba la conexión con la API"""
        try:
            response = self._make_request('games', {'page_size': 1})
            return 'results' in response
        except:
            return False

