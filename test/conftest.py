import pytest
import os
import sys
from dotenv import load_dotenv

# Agregar el directorio raíz al path de Python
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

load_dotenv()

@pytest.fixture
def test_client():
    """Fixture para cliente de prueba de Flask"""
    from app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_session_id():
    """Fixture para ID de sesión de prueba"""
    return "test-session-123"

@pytest.fixture
def mock_database():
    """Fixture para base de datos de prueba"""
    # Para pruebas que no requieren DB real
    class MockDatabase:
        def test_connection(self):
            return True
        def save_conversation(self, *args, **kwargs):
            return True
    return MockDatabase()
