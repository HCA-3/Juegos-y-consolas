"""
Cliente para IGDB (Internet Game Database) API
"""
import requests
import time
from typing import Dict, List, Optional

class IGDBClient:
    """Cliente para interactuar con IGDB API"""
    
    def __init__(self, client_id: Optional[str] = None, access_token: Optional[str] = None):
        self.base_url = "https://api.igdb.com/v4"
        self.client_id = client_id
        self.access_token = access_token
        self.session = requests.Session()
        self.last_request_time = 0
        self.rate_limit_delay = 0.25  # 4 requests per second = 0.25 seconds between requests
        
        # Configurar headers si tenemos credenciales
        if self.client_id and self.access_token:
            self.session.headers.update({
                'Client-ID': self.client_id,
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            })
    
    def _make_request(self, endpoint: str, body: str = "fields *;") -> List[Dict]:
        """Realiza una petición HTTP con rate limiting"""
        if not self.client_id or not self.access_token:
            print("IGDB API requiere Client ID y Access Token")
            return []
        
        # Rate limiting
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last_request)
        
        # Realizar petición
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.post(url, data=body)
            response.raise_for_status()
            self.last_request_time = time.time()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error en petición a IGDB API: {e}")
            return []
    
    def buscar_juegos(self, query: str, limit: int = 20) -> List[Dict]:
        """Busca juegos por nombre"""
        body = f'search "{query}"; fields name,summary,rating,first_release_date,genres.name,platforms.name,involved_companies.company.name,cover.url; limit {limit};'
        return self._make_request('games', body)
    
    def obtener_juego_por_id(self, game_id: int) -> List[Dict]:
        """Obtiene detalles de un juego específico"""
        body = f'fields *; where id = {game_id};'
        return self._make_request('games', body)
    
    def obtener_juegos_populares(self, limit: int = 20) -> List[Dict]:
        """Obtiene juegos populares ordenados por rating"""
        body = f'fields name,summary,rating,first_release_date,genres.name,platforms.name,involved_companies.company.name,cover.url; sort rating desc; limit {limit};'
        return self._make_request('games', body)
    
    def obtener_plataformas(self, limit: int = 50) -> List[Dict]:
        """Obtiene lista de plataformas"""
        body = f'fields name,category,generation; limit {limit};'
        return self._make_request('platforms', body)
    
    def obtener_generos(self, limit: int = 50) -> List[Dict]:
        """Obtiene lista de géneros"""
        body = f'fields name; limit {limit};'
        return self._make_request('genres', body)
    
    def obtener_companias(self, limit: int = 50) -> List[Dict]:
        """Obtiene lista de compañías"""
        body = f'fields name,description; limit {limit};'
        return self._make_request('companies', body)
    
    def convertir_a_modelo_juego(self, igdb_game: Dict) -> Dict:
        """Convierte un juego de IGDB al formato de nuestro modelo"""
        try:
            # Extraer géneros
            generos = []
            if igdb_game.get('genres'):
                generos = [g.get('name', '') for g in igdb_game['genres']]
            
            # Extraer plataformas
            plataformas = []
            if igdb_game.get('platforms'):
                plataformas = [p.get('name', '') for p in igdb_game['platforms']]
            
            # Extraer compañías (desarrolladores/editores)
            desarrolladores = []
            editores = []
            if igdb_game.get('involved_companies'):
                for company in igdb_game['involved_companies']:
                    if company.get('company', {}).get('name'):
                        name = company['company']['name']
                        if company.get('developer'):
                            desarrolladores.append(name)
                        if company.get('publisher'):
                            editores.append(name)
            
            # Convertir fecha de lanzamiento
            fecha_lanzamiento = None
            if igdb_game.get('first_release_date'):
                import datetime
                fecha_lanzamiento = datetime.datetime.fromtimestamp(igdb_game['first_release_date']).date()
            
            # Extraer URL de imagen
            imagen_url = ''
            if igdb_game.get('cover', {}).get('url'):
                imagen_url = f"https:{igdb_game['cover']['url']}"
            
            return {
                'nombre': igdb_game.get('name', ''),
                'genero': ', '.join(generos) if generos else 'No especificado',
                'plataforma': ', '.join(plataformas) if plataformas else 'No especificado',
                'desarrollador': ', '.join(desarrolladores) if desarrolladores else 'No especificado',
                'editor': ', '.join(editores) if editores else 'No especificado',
                'fecha_lanzamiento': fecha_lanzamiento,
                'precio': None,  # IGDB no proporciona precios
                'calificacion': igdb_game.get('rating'),
                'descripcion': igdb_game.get('summary', ''),
                'imagen_url': imagen_url,
                'api_id': str(igdb_game.get('id', ''))
            }
        except Exception as e:
            print(f"Error convirtiendo juego de IGDB: {e}")
            return {}
    
    def convertir_a_modelo_consola(self, igdb_platform: Dict) -> Dict:
        """Convierte una plataforma de IGDB al formato de nuestro modelo de consola"""
        try:
            # Mapear categorías de IGDB a tipos
            category_map = {
                1: 'sobremesa',      # Console
                2: 'arcade',         # Arcade
                3: 'plataforma',     # Platform
                4: 'sistema',        # Operating System
                5: 'portátil',       # Portable Console
                6: 'computadora'     # Computer
            }
            
            tipo = category_map.get(igdb_platform.get('category', 1), 'sobremesa')
            
            return {
                'nombre': igdb_platform.get('name', ''),
                'fabricante': 'No especificado',  # IGDB no siempre tiene esta info
                'generacion': igdb_platform.get('generation'),
                'fecha_lanzamiento': None,  # Requiere consulta adicional
                'precio': None,
                'tipo': tipo,
                'almacenamiento': 'No especificado',
                'procesador': 'No especificado',
                'memoria': 'No especificado',
                'descripcion': '',
                'imagen_url': '',
                'api_id': str(igdb_platform.get('id', ''))
            }
        except Exception as e:
            print(f"Error convirtiendo plataforma de IGDB: {e}")
            return {}
    
    def test_connection(self) -> bool:
        """Prueba la conexión con la API"""
        if not self.client_id or not self.access_token:
            return False
        
        try:
            response = self._make_request('games', 'fields name; limit 1;')
            return len(response) > 0
        except:
            return False

