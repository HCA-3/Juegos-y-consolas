"""
Administrador de APIs externas para el sistema de videojuegos
"""
from typing import Dict, List, Optional
from src.api.rawg_client import RAWGClient
from src.api.igdb_client import IGDBClient
from src.api.mock_client import MockGameClient
from src.models import db, Juego, Consola, HistorialAccion

class APIManager:
    """Administrador centralizado para todas las APIs externas"""
    
    def __init__(self, rawg_api_key: Optional[str] = None, 
                 igdb_client_id: Optional[str] = None, 
                 igdb_access_token: Optional[str] = None,
                 use_mock: bool = False):
        self.rawg_client = RAWGClient(rawg_api_key)
        self.igdb_client = IGDBClient(igdb_client_id, igdb_access_token)
        self.mock_client = MockGameClient()
        self.use_mock = use_mock
        
        # Si no hay credenciales válidas, usar mock automáticamente
        if not rawg_api_key and not (igdb_client_id and igdb_access_token):
            self.use_mock = True
        
    def test_connections(self) -> Dict[str, bool]:
        """Prueba las conexiones con todas las APIs"""
        if self.use_mock:
            return {
                'rawg': False,
                'igdb': False,
                'mock': True
            }
        
        return {
            'rawg': self.rawg_client.test_connection(),
            'igdb': self.igdb_client.test_connection(),
            'mock': False
        }
    
    def buscar_juegos_externos(self, query: str, fuente: str = 'auto') -> List[Dict]:
        """Busca juegos en APIs externas"""
        if self.use_mock or fuente == 'mock':
            response = self.mock_client.buscar_juegos(query)
            if response.get('results'):
                return [self.mock_client.convertir_a_modelo_juego(game) 
                       for game in response['results']]
        elif fuente == 'rawg':
            response = self.rawg_client.buscar_juegos(query)
            if response.get('results'):
                return [self.rawg_client.convertir_a_modelo_juego(game) 
                       for game in response['results']]
        elif fuente == 'igdb':
            games = self.igdb_client.buscar_juegos(query)
            return [self.igdb_client.convertir_a_modelo_juego(game) for game in games]
        
        return []
    
    def obtener_juegos_populares_externos(self, fuente: str = 'auto', limit: int = 20) -> List[Dict]:
        """Obtiene juegos populares de APIs externas"""
        if self.use_mock or fuente == 'mock':
            response = self.mock_client.obtener_juegos_populares(page_size=limit)
            if response.get('results'):
                return [self.mock_client.convertir_a_modelo_juego(game) 
                       for game in response['results']]
        elif fuente == 'rawg':
            response = self.rawg_client.obtener_juegos_populares(page_size=limit)
            if response.get('results'):
                return [self.rawg_client.convertir_a_modelo_juego(game) 
                       for game in response['results']]
        elif fuente == 'igdb':
            games = self.igdb_client.obtener_juegos_populares(limit)
            return [self.igdb_client.convertir_a_modelo_juego(game) for game in games]
        
        return []
    
    def sincronizar_juego_desde_api(self, api_id: str, fuente: str = 'auto') -> Optional[Juego]:
        """Sincroniza un juego específico desde una API externa a la base de datos"""
        try:
            # Obtener datos del juego desde la API
            if self.use_mock or fuente == 'mock':
                game_data = self.mock_client.obtener_juego_por_id(int(api_id))
                if not game_data:
                    return None
                converted_data = self.mock_client.convertir_a_modelo_juego(game_data)
            elif fuente == 'rawg':
                game_data = self.rawg_client.obtener_juego_por_id(int(api_id))
                if not game_data:
                    return None
                converted_data = self.rawg_client.convertir_a_modelo_juego(game_data)
            elif fuente == 'igdb':
                games = self.igdb_client.obtener_juego_por_id(int(api_id))
                if not games:
                    return None
                converted_data = self.igdb_client.convertir_a_modelo_juego(games[0])
            else:
                return None
            
            if not converted_data:
                return None
            
            # Verificar si el juego ya existe
            existing_game = Juego.query.filter_by(api_id=api_id).first()
            
            if existing_game:
                # Actualizar juego existente
                datos_anteriores = existing_game.to_dict()
                
                for key, value in converted_data.items():
                    if hasattr(existing_game, key) and value is not None:
                        setattr(existing_game, key, value)
                
                db.session.commit()
                
                # Registrar en historial
                HistorialAccion.registrar_accion(
                    tabla='juegos',
                    registro_id=existing_game.id,
                    accion='UPDATE',
                    datos_anteriores=datos_anteriores,
                    datos_nuevos=existing_game.to_dict(),
                    usuario='api_sync'
                )
                
                return existing_game
            else:
                # Crear nuevo juego
                nuevo_juego = Juego(**converted_data)
                db.session.add(nuevo_juego)
                db.session.commit()
                
                # Registrar en historial
                HistorialAccion.registrar_accion(
                    tabla='juegos',
                    registro_id=nuevo_juego.id,
                    accion='CREATE',
                    datos_nuevos=nuevo_juego.to_dict(),
                    usuario='api_sync'
                )
                
                return nuevo_juego
                
        except Exception as e:
            print(f"Error sincronizando juego desde API: {e}")
            db.session.rollback()
            return None
    
    def sincronizar_juegos_populares(self, fuente: str = 'auto', limit: int = 10) -> List[Juego]:
        """Sincroniza juegos populares desde una API externa"""
        juegos_sincronizados = []
        
        try:
            # Obtener juegos populares
            if self.use_mock or fuente == 'mock':
                response = self.mock_client.obtener_juegos_populares(page_size=limit)
                if response.get('results'):
                    for game_data in response['results']:
                        api_id = str(game_data.get('id'))
                        if api_id:
                            juego = self.sincronizar_juego_desde_api(api_id, 'mock')
                            if juego:
                                juegos_sincronizados.append(juego)
            elif fuente == 'rawg':
                response = self.rawg_client.obtener_juegos_populares(page_size=limit)
                if response.get('results'):
                    for game_data in response['results']:
                        api_id = str(game_data.get('id'))
                        if api_id:
                            juego = self.sincronizar_juego_desde_api(api_id, fuente)
                            if juego:
                                juegos_sincronizados.append(juego)
            elif fuente == 'igdb':
                games = self.igdb_client.obtener_juegos_populares(limit)
                for game_data in games:
                    api_id = str(game_data.get('id'))
                    if api_id:
                        juego = self.sincronizar_juego_desde_api(api_id, fuente)
                        if juego:
                            juegos_sincronizados.append(juego)
            
        except Exception as e:
            print(f"Error sincronizando juegos populares: {e}")
        
        return juegos_sincronizados
    
    def obtener_plataformas_externas(self, fuente: str = 'auto') -> List[Dict]:
        """Obtiene plataformas desde APIs externas"""
        if self.use_mock or fuente == 'mock':
            response = self.mock_client.obtener_plataformas()
            if response.get('results'):
                return response['results']
        elif fuente == 'rawg':
            response = self.rawg_client.obtener_plataformas()
            if response.get('results'):
                return response['results']
        elif fuente == 'igdb':
            platforms = self.igdb_client.obtener_plataformas()
            return [self.igdb_client.convertir_a_modelo_consola(platform) for platform in platforms]
        
        return []
    
    def obtener_generos_externos(self, fuente: str = 'auto') -> List[Dict]:
        """Obtiene géneros desde APIs externas"""
        if self.use_mock or fuente == 'mock':
            response = self.mock_client.obtener_generos()
            if response.get('results'):
                return response['results']
        elif fuente == 'rawg':
            response = self.rawg_client.obtener_generos()
            if response.get('results'):
                return response['results']
        elif fuente == 'igdb':
            return self.igdb_client.obtener_generos()
        
        return []
    
    def buscar_y_sugerir_juegos(self, query: str) -> Dict[str, List[Dict]]:
        """Busca juegos en todas las APIs y devuelve sugerencias"""
        resultados = {}
        
        if self.use_mock:
            # Usar solo datos mock
            try:
                mock_results = self.buscar_juegos_externos(query, 'mock')
                resultados['mock'] = mock_results[:5]  # Limitar a 5 resultados
            except Exception as e:
                print(f"Error buscando en mock: {e}")
                resultados['mock'] = []
        else:
            # Buscar en RAWG
            try:
                rawg_results = self.buscar_juegos_externos(query, 'rawg')
                resultados['rawg'] = rawg_results[:5]  # Limitar a 5 resultados
            except Exception as e:
                print(f"Error buscando en RAWG: {e}")
                resultados['rawg'] = []
            
            # Buscar en IGDB (si está configurado)
            try:
                if self.igdb_client.client_id and self.igdb_client.access_token:
                    igdb_results = self.buscar_juegos_externos(query, 'igdb')
                    resultados['igdb'] = igdb_results[:5]  # Limitar a 5 resultados
                else:
                    resultados['igdb'] = []
            except Exception as e:
                print(f"Error buscando en IGDB: {e}")
                resultados['igdb'] = []
        
        return resultados
    
    def importar_juego_desde_sugerencia(self, datos_juego: Dict, fuente: str) -> Optional[Juego]:
        """Importa un juego desde una sugerencia de API externa"""
        try:
            # Verificar si el juego ya existe por API ID
            api_id = datos_juego.get('api_id')
            if api_id:
                existing_game = Juego.query.filter_by(api_id=api_id).first()
                if existing_game:
                    return existing_game
            
            # Crear nuevo juego
            nuevo_juego = Juego(**datos_juego)
            db.session.add(nuevo_juego)
            db.session.commit()
            
            # Registrar en historial
            HistorialAccion.registrar_accion(
                tabla='juegos',
                registro_id=nuevo_juego.id,
                accion='CREATE',
                datos_nuevos=nuevo_juego.to_dict(),
                usuario='api_import'
            )
            
            return nuevo_juego
            
        except Exception as e:
            print(f"Error importando juego desde sugerencia: {e}")
            db.session.rollback()
            return None

