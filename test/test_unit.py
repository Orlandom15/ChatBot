import pytest
import sys
import os

# Agregar config al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))

class TestChatbotUnit:
    """Pruebas unitarias para el chatbot"""
    
    def test_message_processing(self):
        """Probar procesamiento básico de mensajes"""
        from app import process_message
        
        response, intent, confidence = process_message("hola")
        assert intent == "greeting"
        assert confidence > 0.5
        assert "Hola" in response
    
    def test_message_filtering_should_save(self):
        """Probar filtrado de mensajes - debería guardar"""
        from database import NeonDatabase
        
        db = NeonDatabase()
        # Mensaje valioso debería guardarse
        assert db._should_save_message("Necesito información de servicios", "services") == True
        assert db._should_save_message("¿Cuál es su horario de atención?", "hours") == True
    
    def test_message_filtering_should_not_save(self):
        """Probar filtrado de mensajes - NO debería guardar"""
        from database import NeonDatabase
        
        db = NeonDatabase()
        # Mensajes genéricos NO deberían guardarse
        assert db._should_save_message("hola", "greeting") == False
        assert db._should_save_message("ok", "generic") == False
        assert db._should_save_message("gracias", "thanks") == False
    
    def test_intent_detection(self):
        """Probar detección de intenciones"""
        from database import NeonDatabase
        
        db = NeonDatabase()
        
        # Probar diferentes mensajes
        test_cases = [
            ("hola", "greeting"),
            ("servicios", "services"),
            ("contacto", "contact"),
            ("horario", "hours"),
        ]
        
        for message, expected_intent in test_cases:
            response, intent, confidence = db.get_bot_response(message)
            assert intent == expected_intent
            assert confidence > 0.5
            assert len(response) > 0

class TestDatabaseUnit:
    """Pruebas unitarias para la base de datos"""
    
    def test_database_connection(self):
        """Probar que la conexión a la base de datos funciona"""
        from database import NeonDatabase
        
        db = NeonDatabase()
        # Esto probará la conexión real a Neon.tech
        assert db.test_connection() == True
    
    def test_session_management(self, sample_session_id):
        """Probar gestión de sesiones"""
        from database import NeonDatabase
        
        db = NeonDatabase()
        
        # Probar guardar conversación
        result = db.save_conversation(
            sample_session_id,
            "Mensaje de prueba",
            "Respuesta de prueba",
            "test",
            0.8
        )
        assert result == True
        
        # Probar obtener historial
        history = db.get_chat_history(sample_session_id)
        assert isinstance(history, list)