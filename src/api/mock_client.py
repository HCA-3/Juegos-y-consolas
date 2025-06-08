"""
Cliente simulado para datos de videojuegos (para desarrollo sin APIs externas)
"""
from typing import Dict, List, Optional
import random
from datetime import datetime, date

class MockGameClient:
    """Cliente simulado que proporciona datos de prueba para videojuegos"""
    
    def __init__(self):
        self.juegos_mock = [
            {
                'id': 1,
                'name': 'Cyberpunk 2077',
                'genres': [{'name': 'RPG'}, {'name': 'Acción'}],
                'platforms': [{'platform': {'name': 'PC'}}, {'platform': {'name': 'PlayStation 5'}}],
                'developers': [{'name': 'CD Projekt RED'}],
                'publishers': [{'name': 'CD Projekt'}],
                'released': '2020-12-10',
                'rating': 4.2,
                'description_raw': 'Un RPG de acción de mundo abierto ambientado en Night City.',
                'background_image': 'https://media.rawg.io/media/games/26d/26d4437715bee60138dab4a7c8c59c92.jpg'
            },
            {
                'id': 2,
                'name': 'The Witcher 3: Wild Hunt',
                'genres': [{'name': 'RPG'}, {'name': 'Aventura'}],
                'platforms': [{'platform': {'name': 'PC'}}, {'platform': {'name': 'PlayStation 4'}}],
                'developers': [{'name': 'CD Projekt RED'}],
                'publishers': [{'name': 'CD Projekt'}],
                'released': '2015-05-19',
                'rating': 4.7,
                'description_raw': 'Un RPG de fantasía épica con una historia envolvente.',
                'background_image': 'https://media.rawg.io/media/games/618/618c2031a07bbff6b4f611f10b6bcdbc.jpg'
            },
            {
                'id': 3,
                'name': 'Grand Theft Auto V',
                'genres': [{'name': 'Acción'}, {'name': 'Aventura'}],
                'platforms': [{'platform': {'name': 'PC'}}, {'platform': {'name': 'PlayStation 5'}}],
                'developers': [{'name': 'Rockstar North'}],
                'publishers': [{'name': 'Rockstar Games'}],
                'released': '2013-09-17',
                'rating': 4.5,
                'description_raw': 'Un juego de acción y aventura en mundo abierto.',
                'background_image': 'https://media.rawg.io/media/games/456/456dea5e1c7e3cd07060c14e96612001.jpg'
            },
            {
                'id': 4,
                'name': 'The Legend of Zelda: Breath of the Wild',
                'genres': [{'name': 'Aventura'}, {'name': 'RPG'}],
                'platforms': [{'platform': {'name': 'Nintendo Switch'}}],
                'developers': [{'name': 'Nintendo EPD'}],
                'publishers': [{'name': 'Nintendo'}],
                'released': '2017-03-03',
                'rating': 4.8,
                'description_raw': 'Una aventura épica en el reino de Hyrule.',
                'background_image': 'https://media.rawg.io/media/games/cc1/cc196a5ad763955d6532cdba236f730c.jpg'
            },
            {
                'id': 5,
                'name': 'FIFA 23',
                'genres': [{'name': 'Deportes'}],
                'platforms': [{'platform': {'name': 'PC'}}, {'platform': {'name': 'PlayStation 5'}}],
                'developers': [{'name': 'EA Sports'}],
                'publishers': [{'name': 'Electronic Arts'}],
                'released': '2022-09-30',
                'rating': 3.8,
                'description_raw': 'El simulador de fútbol más realista.',
                'background_image': 'https://media.rawg.io/media/games/d63/d63afe80c8fe5e2a0d0e4b4e5f0c8e8a.jpg'
            }
        ]
        
        self.consolas_mock = [
            {
                'id': 1,
                'name': 'PlayStation 5',
                'category': 1,  # Console
                'generation': 9
            },
            {
                'id': 2,
                'name': 'Xbox Series X',
                'category': 1,  # Console
                'generation': 9
            },
            {
                'id': 3,
                'name': 'Nintendo Switch',
                'category': 5,  # Portable Console
                'generation': 8
            }
        ]
        
        self.generos_mock = [
            {'id': 1, 'name': 'Acción'},
            {'id': 2, 'name': 'Aventura'},
            {'id': 3, 'name': 'RPG'},
            {'id': 4, 'name': 'Deportes'},
            {'id': 5, 'name': 'Estrategia'},
            {'id': 6, 'name': 'Simulación'}
        ]
    
    def buscar_juegos(self, query: str, page: int = 1, page_size: int = 20) -> Dict:
        """Simula búsqueda de juegos"""
        query_lower = query.lower()
        resultados = [
            juego for juego in self.juegos_mock 
            if query_lower in juego['name'].lower()
        ]
        
        return {
            'count': len(resultados),
            'results': resultados[:page_size]
        }
    
    def obtener_juego_por_id(self, game_id: int) -> Dict:
        """Simula obtener juego por ID"""
        for juego in self.juegos_mock:
            if juego['id'] == game_id:
                return juego
        return {}
    
    def obtener_juegos_populares(self, page: int = 1, page_size: int = 20) -> Dict:
        """Simula obtener juegos populares"""
        # Ordenar por rating descendente
        juegos_ordenados = sorted(self.juegos_mock, key=lambda x: x['rating'], reverse=True)
        
        return {
            'count': len(juegos_ordenados),
            'results': juegos_ordenados[:page_size]
        }
    
    def obtener_plataformas(self, page: int = 1, page_size: int = 20) -> Dict:
        """Simula obtener plataformas"""
        return {
            'count': len(self.consolas_mock),
            'results': self.consolas_mock[:page_size]
        }
    
    def obtener_generos(self, page: int = 1, page_size: int = 20) -> Dict:
        """Simula obtener géneros"""
        return {
            'count': len(self.generos_mock),
            'results': self.generos_mock[:page_size]
        }
    
    def convertir_a_modelo_juego(self, mock_game: Dict) -> Dict:
        """Convierte un juego mock al formato de nuestro modelo"""
        try:
            # Extraer plataformas
            plataformas = []
            if mock_game.get('platforms'):
                plataformas = [p['platform']['name'] for p in mock_game['platforms']]
            
            # Extraer géneros
            generos = []
            if mock_game.get('genres'):
                generos = [g['name'] for g in mock_game['genres']]
            
            # Extraer desarrolladores
            desarrolladores = []
            if mock_game.get('developers'):
                desarrolladores = [d['name'] for d in mock_game['developers']]
            
            # Extraer editores
            editores = []
            if mock_game.get('publishers'):
                editores = [p['name'] for p in mock_game['publishers']]
            
            return {
                'nombre': mock_game.get('name', ''),
                'genero': ', '.join(generos) if generos else 'No especificado',
                'plataforma': ', '.join(plataformas) if plataformas else 'No especificado',
                'desarrollador': ', '.join(desarrolladores) if desarrolladores else 'No especificado',
                'editor': ', '.join(editores) if editores else 'No especificado',
                'fecha_lanzamiento': mock_game.get('released'),
                'precio': round(random.uniform(19.99, 69.99), 2),  # Precio aleatorio
                'calificacion': mock_game.get('rating'),
                'descripcion': mock_game.get('description_raw', ''),
                'imagen_url': mock_game.get('background_image', ''),
                'api_id': str(mock_game.get('id', ''))
            }
        except Exception as e:
            print(f"Error convirtiendo juego mock: {e}")
            return {}
    
    def test_connection(self) -> bool:
        """Simula prueba de conexión"""
        return True

