import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

class NeonDatabase:
    def __init__(self):
        # ✅ Usando tu Connection String directo de Neon
        self.db_url = 'postgresql://neondb_owner:npg_VucFrN1XpB4O@ep-jolly-bush-ad1cfyvj-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
        
        # Mostrar solo el host para seguridad
        safe_url = self.db_url.split('@')[1] if '@' in self.db_url else 'URL no válida'
        print(f"🔧 Conectando a: {safe_url}")
    
    def get_connection(self):
        """Obtener conexión a Neon.tech"""
        try:
            conn = psycopg2.connect(
                self.db_url,
                cursor_factory=RealDictCursor,
                keepalives=1,
                keepalives_idle=30,
                keepalives_interval=10,
                keepalives_count=5
            )
            return conn
        except Exception as e:
            print(f"❌ Error conectando a Neon: {e}")
            raise
    
    def test_connection(self):
        """Probar que la conexión funciona y las tablas existen"""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            # Información básica de la BD
            cur.execute('SELECT version();')
            version = cur.fetchone()
            
            cur.execute('SELECT current_database();')
            db_name = cur.fetchone()
            
            # Verificar que las tablas existen
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            tables = [row['table_name'] for row in cur.fetchall()]
            
            print(f"🐘 PostgreSQL: {version['version'].split(',')[0]}")
            print(f"🗃️ Base de datos: {db_name['current_database']}")
            print(f"📊 Tablas existentes: {', '.join(tables)}")
            
            cur.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error en test de conexión: {e}")
            return False

    def get_bot_response(self, user_message):
        """Obtener respuesta del bot - VERSIÓN COMPLETAMENTE CORREGIDA"""
        try:
            user_lower = user_message.lower().strip()
            print(f"   🔍 Analizando: '{user_lower}'")
            
            # PRIMERO: Verificar qué hay en la base de datos
            conn = self.get_connection()
            cur = conn.cursor()
            
            print("   📊 CONSULTANDO common_intents...")
            
            # DEPURACIÓN: Ver todos los datos de common_intents
            cur.execute('SELECT intent_name, example_questions, response_template FROM common_intents ORDER BY intent_name')
            
            all_intents = cur.fetchall()
            print(f"   📋 Intenciones en BD: {len(all_intents)}")
            
            for intent in all_intents:
                question_count = len(intent['example_questions']) if intent['example_questions'] else 0
                print(f"      - {intent['intent_name']}: {question_count} preguntas")
            
            # Método 1: Buscar por palabras en example_questions - CONSULTA SIMPLIFICADA
            print(f"   🔎 Buscando coincidencias para: '{user_lower}'")
            
            # CONSULTA CORREGIDA - sin parámetros problemáticos
            query = f"""
            SELECT intent_name, response_template 
            FROM common_intents 
            WHERE EXISTS (
                SELECT 1 
                FROM unnest(example_questions) AS question 
                WHERE '{user_lower}' ILIKE '%' || question || '%'
            )
            LIMIT 1
            """
            
            cur.execute(query)
            intent_data = cur.fetchone()
            
            if intent_data:
                print(f"   ✅ Intención ENCONTRADA en BD: {intent_data['intent_name']}")
                print(f"   💬 Respuesta: {intent_data['response_template'][:50]}...")
                cur.close()
                conn.close()
                return intent_data['response_template'], intent_data['intent_name'], 0.9
            
            print("   ❌ No se encontró coincidencia exacta en example_questions")
            
           
            keywords_mapping = {
                'hola': 'greeting',
                'servicio': 'services', 
                'contacto': 'contact',
                'horario': 'hours',
                'ubicación': 'location',
                'precio': 'pricing',
                'gracias': 'thanks',
                'adiós': 'goodbye'
            }
            
            detected_intent = 'default'
            for keyword, intent in keywords_mapping.items():
                if keyword in user_lower:
                    detected_intent = intent
                    print(f"   🎯 Intención detectada por keyword: {detected_intent}")
                    break
            
            # Obtener respuesta para la intención detectada - CONSULTA SIMPLIFICADA
            query2 = f"SELECT response_template FROM common_intents WHERE intent_name = '{detected_intent}'"
            cur.execute(query2)
            intent_response = cur.fetchone()
            
            cur.close()
            conn.close()
            
            if intent_response:
                print(f"   ✅ Respuesta obtenida de BD para: {detected_intent}")
                return intent_response['response_template'], detected_intent, 0.7
            
            # Si llegamos aquí, usar respuesta local de respaldo
            print("   ⚠️  Usando respuesta local de respaldo")
            responses_map = {
                'hola': ("¡Hola! ¿En qué puedo ayudarte?", "greeting", 0.9),
                'servicios': ("Ofrecemos servicios de consultoría tecnológica, desarrollo de software y soporte técnico. ¿Te interesa algún servicio en particular?", "services", 0.9),
                'contacto': ("Puedes contactarnos en info@recioymendoza.com o llamando al +52 656 123 4567", "contact", 0.9),
                'horario': ("Nuestro horario de atención es de lunes a viernes de 9:00 a 18:00 horas", "hours", 0.9),
                'ubicación': ("Estamos ubicados en Calle Principal 123, Juárez, Chihuahua, México", "location", 0.9),
                'precio': ("Los precios varían según el servicio. ¿Podrías especificar qué servicio te interesa?", "pricing", 0.9),
            }
            
            for keyword, (response, intent, confidence) in responses_map.items():
                if keyword in user_lower:
                    print(f"   🎯 Intención local: {intent}")
                    return response, intent, confidence
            
            # Respuesta por defecto
            default_response = "¡Hola! Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?"
            print("   🎯 Intención: default")
            return default_response, "default", 0.5
            
        except Exception as e:
            print(f"❌ ERROR en get_bot_response: {str(e)}")
            import traceback
            print(f"❌ TRAZA COMPLETA: {traceback.format_exc()}")
            
            # Respuesta de fallback ULTRA simple
            fallback_response = "¡Hola! ¿En qué puedo ayudarte?"
            return fallback_response, "error", 0.0

    def save_conversation(self, session_id, user_message, bot_response, intent=None, confidence=0.0):
        """Guardar conversación en la base de datos - VERSIÓN SIMPLIFICADA"""
        try:
            # ✅ Solo guardar mensajes valiosos
            if not self._should_save_message(user_message, intent):
                print(f"📝 No guardado (mensaje genérico): {user_message}")
                return True
            
            conn = self.get_connection()
            cur = conn.cursor()
            
            # SOLO guardar en chat_messages (evitar analytics por ahora)
            cur.execute('''
                INSERT INTO chat_messages 
                (session_id, message_type, user_message, bot_response, intent_detected, confidence)
                VALUES (%s, 'user', %s, %s, %s, %s)
            ''', (session_id, user_message, bot_response, intent, confidence))
            
            conn.commit()
            cur.close()
            conn.close()
            
            print(f"💾 Conversación guardada - Sesión: {session_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error guardando conversación: {e}")
            return False

    def _should_save_message(self, user_message, intent):
        """Determinar si vale la pena guardar el mensaje"""
        message_lower = user_message.lower().strip()
        
        # ❌ NO guardar mensajes muy cortos o genéricos
        dont_save_messages = {
            'hola', 'hola!', 'hi', 'hello', 
            'gracias', 'thanks', 'ok', 'okay', 'vale',
            'adiós', 'bye', 'chao', 'nos vemos', 'bueno',
            'sí', 'no', 'ja', 'jaja', 'jajaja'
        }
        
        if message_lower in dont_save_messages:
            return False
        
        if len(user_message.strip()) < 3:
            return False
        
        # ✅ SÍ guardar mensajes con intenciones valiosas
        valuable_intents = {'services', 'contact', 'hours', 'location', 'pricing'}
        if intent in valuable_intents:
            return True
        
        # ✅ SÍ guardar mensajes largos (preguntas reales)
        if len(user_message) > 15:
            return True
        
        return False

    def get_chat_history(self, session_id, limit=20):
        """Obtener historial de chat para una sesión"""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            cur.execute('''
                SELECT 
                    message_type,
                    user_message,
                    bot_response,
                    intent_detected,
                    created_at
                FROM chat_messages 
                WHERE session_id = %s 
                ORDER BY created_at DESC
                LIMIT %s
            ''', (session_id, limit))
            
            messages = cur.fetchall()
            cur.close()
            conn.close()
            
            return list(reversed(messages))  # Ordenar de más viejo a más nuevo
            
        except Exception as e:
            print(f"❌ Error obteniendo historial: {e}")
            return []

    def get_analytics(self):
        """Obtener analytics básicos del chatbot"""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            # Mensajes totales
            cur.execute('SELECT COUNT(*) as total_messages FROM chat_messages')
            total_messages = cur.fetchone()['total_messages']
            
            # Sesiones únicas
            cur.execute('SELECT COUNT(DISTINCT session_id) as unique_sessions FROM chat_messages')
            unique_sessions = cur.fetchone()['unique_sessions']
            
            cur.close()
            conn.close()
            
            return {
                'total_messages': total_messages,
                'unique_sessions': unique_sessions,
                'top_intents': []  # Simplificado por ahora
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo analytics: {e}")
            return {}