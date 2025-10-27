import pytest
import json

class TestChatbotIntegration:
    """Pruebas de integración para el chatbot"""
    
    def test_chat_endpoint(self, test_client):
        """Probar el endpoint /api/chat"""
        # Preparar datos de prueba
        test_data = {
            "message": "hola",
            "session_id": "test-session-integration"
        }
        
        # Hacer petición POST
        response = test_client.post(
            '/api/chat',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        # Verificar respuesta
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'response' in data
        assert 'session_id' in data
        assert 'intent' in data
        assert len(data['response']) > 0
    
    def test_chat_endpoint_invalid_data(self, test_client):
        """Probar el endpoint con datos inválidos"""
        # Datos inválidos
        response = test_client.post(
            '/api/chat',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_home_endpoint(self, test_client):
        """Probar el endpoint raíz"""
        response = test_client.get('/')
        assert response.status_code == 200
        assert b'ChatBot' in response.data
    
    def test_multiple_messages(self, test_client):
        """Probar múltiples mensajes en la misma sesión"""
        session_id = "test-session-multiple"
        
        messages = [
            "hola",
            "¿qué servicios ofrecen?",
            "gracias"
        ]
        
        for message in messages:
            response = test_client.post(
                '/api/chat',
                data=json.dumps({
                    "message": message,
                    "session_id": session_id
                }),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert 'response' in data

class TestDatabaseIntegration:
    """Pruebas de integración con la base de datos real"""
    
    def test_real_database_operations(self, sample_session_id):
        """Probar operaciones reales con la base de datos"""
        from database import NeonDatabase
        
        db = NeonDatabase()
        
        # Probar conexión
        assert db.test_connection() == True
        
        # Probar guardar y recuperar historial
        test_message = "Mensaje de prueba de integración"
        test_response = "Respuesta de prueba de integración"
        
        # Guardar
        save_result = db.save_conversation(
            sample_session_id,
            test_message,
            test_response,
            "test",
            0.9
        )
        assert save_result == True
        
        # Recuperar historial
        history = db.get_chat_history(sample_session_id)
        assert len(history) > 0
        
        # Verificar que el mensaje está en el historial
        found = False
        for msg in history:
            if msg.get('user_message') == test_message:
                found = True
                break
        
        assert found == True