"""
Script de prueba para las APIs externas
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.api.rawg_client import RAWGClient
from src.api.igdb_client import IGDBClient
from src.api.api_manager import APIManager

def test_rawg_api():
    """Prueba la API de RAWG"""
    print("=== Probando RAWG API ===")
    
    client = RAWGClient()
    
    # Probar conexión
    if client.test_connection():
        print("✓ Conexión exitosa con RAWG API")
    else:
        print("✗ Error conectando con RAWG API")
        return
    
    # Buscar juegos
    print("\nBuscando 'Cyberpunk'...")
    results = client.buscar_juegos("Cyberpunk", page_size=3)
    if results.get('results'):
        for game in results['results'][:2]:
            converted = client.convertir_a_modelo_juego(game)
            print(f"- {converted.get('nombre', 'N/A')} ({converted.get('genero', 'N/A')})")
    
    # Obtener juegos populares
    print("\nObteniendo juegos populares...")
    popular = client.obtener_juegos_populares(page_size=3)
    if popular.get('results'):
        for game in popular['results'][:2]:
            converted = client.convertir_a_modelo_juego(game)
            print(f"- {converted.get('nombre', 'N/A')} (Rating: {converted.get('calificacion', 'N/A')})")

def test_igdb_api():
    """Prueba la API de IGDB (requiere credenciales)"""
    print("\n=== Probando IGDB API ===")
    
    client = IGDBClient()
    
    if not client.client_id or not client.access_token:
        print("⚠ IGDB API requiere Client ID y Access Token")
        print("  Para obtenerlos:")
        print("  1. Crear cuenta en Twitch")
        print("  2. Registrar aplicación en Twitch Developer Portal")
        print("  3. Obtener Client ID y Client Secret")
        print("  4. Hacer POST a https://id.twitch.tv/oauth2/token")
        return
    
    # Probar conexión
    if client.test_connection():
        print("✓ Conexión exitosa con IGDB API")
    else:
        print("✗ Error conectando con IGDB API")
        return
    
    # Buscar juegos
    print("\nBuscando 'Mario'...")
    results = client.buscar_juegos("Mario", limit=3)
    for game in results[:2]:
        converted = client.convertir_a_modelo_juego(game)
        print(f"- {converted.get('nombre', 'N/A')} ({converted.get('genero', 'N/A')})")

def test_api_manager():
    """Prueba el administrador de APIs"""
    print("\n=== Probando API Manager ===")
    
    # Crear manager que usará mock automáticamente si no hay credenciales
    manager = APIManager()
    
    # Probar conexiones
    connections = manager.test_connections()
    print(f"Conexiones: RAWG={connections.get('rawg', False)}, IGDB={connections.get('igdb', False)}, Mock={connections.get('mock', False)}")
    
    if connections.get('mock', False):
        print("✓ Usando datos simulados para desarrollo")
        
        # Buscar juegos
        print("\nBuscando 'Cyberpunk' en datos simulados...")
        resultados = manager.buscar_y_sugerir_juegos("Cyberpunk")
        
        print(f"Resultados Mock: {len(resultados.get('mock', []))}")
        for game in resultados.get('mock', [])[:2]:
            print(f"  - {game.get('nombre', 'N/A')} ({game.get('genero', 'N/A')})")
        
        # Obtener juegos populares
        print("\nObteniendo juegos populares simulados...")
        populares = manager.obtener_juegos_populares_externos('mock', limit=3)
        for game in populares[:2]:
            print(f"  - {game.get('nombre', 'N/A')} (Rating: {game.get('calificacion', 'N/A')})")
    else:
        # Buscar juegos en APIs reales
        print("\nBuscando 'Zelda' en APIs reales...")
        resultados = manager.buscar_y_sugerir_juegos("Zelda")
        
        print(f"Resultados RAWG: {len(resultados.get('rawg', []))}")
        for game in resultados.get('rawg', [])[:2]:
            print(f"  - {game.get('nombre', 'N/A')}")
        
        print(f"Resultados IGDB: {len(resultados.get('igdb', []))}")
        for game in resultados.get('igdb', [])[:2]:
            print(f"  - {game.get('nombre', 'N/A')}")

if __name__ == "__main__":
    print("Iniciando pruebas de APIs externas...\n")
    
    try:
        test_rawg_api()
        test_igdb_api()
        test_api_manager()
        
        print("\n=== Pruebas completadas ===")
        
    except Exception as e:
        print(f"\nError durante las pruebas: {e}")
        import traceback
        traceback.print_exc()

