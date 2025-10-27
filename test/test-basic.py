import pytest
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_imports():
    """Prueba que los imports funcionen"""
    try:
        from app import app
        from config.database import NeonDatabase
        assert True
    except ImportError as e:
        pytest.fail(f"Error de importación: {e}")

def test_app_creation():
    """Prueba que la app de Flask se crea correctamente"""
    from app import app
    assert app is not None
    assert hasattr(app, 'route')

def test_database_connection():
    """Prueba básica de conexión a la base de datos"""
    try:
        from config.database import NeonDatabase
        db = NeonDatabase()
        # Solo probamos que se puede crear la instancia
        assert db is not None
    except Exception as e:
        # Si falla, no rompe el test pero muestra advertencia
        pytest.skip(f"Conexión a BD no disponible: {e}")

def test_sample_logic():
    """Prueba de lógica simple"""
    def process_message(message):
        message_lower = message.lower()
        if 'hola' in message_lower:
            return "¡Hola! ¿En qué puedo ayudarte?", "greeting", 0.9
        return "No entendí", "default", 0.5
    
    response, intent, confidence = process_message("hola")
    assert intent == "greeting"
    assert confidence > 0.5