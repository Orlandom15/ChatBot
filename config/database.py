import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime

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
        """Obtener respuesta del bot - EXPANDIDO PARA UNIVERSIDAD"""
        try:
            user_lower = user_message.lower().strip()
            print(f"   🔍 Analizando: '{user_lower}'")
            
            # === CONSULTAS UNIVERSITARIAS ===
            if any(palabra in user_lower for palabra in ['estudiante', 'alumno', 'matricula', 'alumnos']):
                return self._procesar_consulta_estudiantes(user_lower)
            
            elif any(palabra in user_lower for palabra in ['total', 'cuántos', 'cuantos', 'estadística', 'estadistica', 'estadísticas']):
                return self._procesar_estadisticas(user_lower)
            
            elif any(palabra in user_lower for palabra in ['inscripción', 'inscripcion', 'pago', 'debe', 'pendiente']):
                return self._procesar_inscripciones(user_lower)
            
            elif any(palabra in user_lower for palabra in ['reporte', 'archivo', 'descargar', 'generar', 'excel']):
                return self._procesar_reportes(user_lower)
            
            elif any(palabra in user_lower for palabra in ['carrera', 'ingeniería', 'sistemas', 'industrial', 'contaduría']):
                return self._procesar_carreras(user_lower)
            
            # Si no es consulta universitaria, usar la lógica normal
            return self._procesar_consulta_normal(user_lower)
            
        except Exception as e:
            print(f"❌ Error en get_bot_response: {str(e)}")
            return "¡Hola! ¿En qué puedo ayudarte con información universitaria?", "error", 0.0

    def _procesar_consulta_normal(self, user_message):
        """Procesar consultas normales del chatbot empresarial"""
        try:
            user_lower = user_message.lower().strip()
            
            # PRIMERO: Verificar qué hay en la base de datos
            conn = self.get_connection()
            cur = conn.cursor()
            
            # Método 1: Buscar por palabras en example_questions
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
                cur.close()
                conn.close()
                return intent_data['response_template'], intent_data['intent_name'], 0.9
            
            # Método 2: Buscar por palabras clave
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
            
            # Obtener respuesta para la intención detectada
            query2 = f"SELECT response_template FROM common_intents WHERE intent_name = '{detected_intent}'"
            cur.execute(query2)
            intent_response = cur.fetchone()
            
            cur.close()
            conn.close()
            
            if intent_response:
                print(f"   ✅ Respuesta obtenida de BD para: {detected_intent}")
                return intent_response['response_template'], detected_intent, 0.7
            
            # Respuesta local de respaldo
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
            print(f"❌ Error en consulta normal: {str(e)}")
            return "¡Hola! ¿En qué puedo ayudarte?", "error", 0.0

    def _procesar_estadisticas(self, user_message):
        """Procesar consultas sobre estadísticas universitarias"""
        try:
            estadisticas = self.get_estadisticas_estudiantes()
            
            if not estadisticas:
                return "No pude obtener las estadísticas en este momento.", "estadisticas", 0.5
            
            respuesta = f"📊 **Estadísticas Universitarias**\n\n"
            respuesta += f"👥 **Total de estudiantes:** {estadisticas['total_estudiantes']}\n"
            respuesta += f"✅ **Inscripción pagada:** {estadisticas['inscritos_pagados']}\n"
            respuesta += f"❌ **Pendientes de pago:** {estadisticas['pendientes_inscripcion']}\n\n"
            
            respuesta += "🎓 **Distribución por carrera:**\n"
            for carrera in estadisticas['por_carrera']:
                respuesta += f"  • {carrera['carrera']}: {carrera['cantidad']} estudiantes\n"
            
            return respuesta, "estadisticas_universidad", 0.9
            
        except Exception as e:
            print(f"❌ Error procesando estadísticas: {e}")
            return "Error obteniendo estadísticas universitarias.", "error", 0.0

    def _procesar_inscripciones(self, user_message):
        """Procesar consultas sobre inscripciones"""
        try:
            if 'pendiente' in user_message or 'debe' in user_message:
                estudiantes = self.get_estudiantes_pendientes_inscripcion()
                
                if not estudiantes:
                    return "🎉 **¡Excelente! No hay estudiantes pendientes de inscripción.**", "inscripciones", 0.9
                
                respuesta = f"📋 **Estudiantes pendientes de inscripción: {len(estudiantes)}**\n\n"
                for i, est in enumerate(estudiantes[:10], 1):
                    estado = "❌ Pendiente"
                    respuesta += f"{i}. **{est['matricula']}** - {est['nombre']} {est['apellido']}\n"
                    respuesta += f"   🎓 {est['carrera']} - Semestre {est['semestre']}\n"
                    respuesta += f"   📅 Inscrito desde: {est['fecha_inscripcion']}\n\n"
                
                if len(estudiantes) > 10:
                    respuesta += f"📝 *Y {len(estudiantes) - 10} estudiantes más...*"
                
                return respuesta, "inscripciones_pendientes", 0.9
            
            return "Puedo ayudarte con información de inscripciones. ¿Quieres saber sobre estudiantes pendientes de pago?", "inscripciones", 0.7
            
        except Exception as e:
            print(f"❌ Error procesando inscripciones: {e}")
            return "Error obteniendo información de inscripciones.", "error", 0.0

    def _procesar_reportes(self, user_message):
        """Procesar solicitudes de reportes"""
        try:
            if 'inscripción' in user_message or 'inscripcion' in user_message:
                reporte = self.generar_reporte_inscripciones()
                
                respuesta = f"📄 **Reporte generado exitosamente**\n\n"
                respuesta += f"• **Tipo:** Inscripciones pendientes\n"
                respuesta += f"• **Estudiantes pendientes:** {reporte['total_pendientes']}\n"
                respuesta += f"• **ID del reporte:** {reporte['reporte_id']}\n"
                respuesta += f"• **Fecha:** {reporte['fecha_generacion'][:10]}\n\n"
                respuesta += "💡 *El reporte está listo para descargar*"
                
                return respuesta, "reporte_generado", 0.9
            
            return "Puedo generar reportes de: inscripciones pendientes, estudiantes por carrera, estadísticas generales.", "reportes", 0.8
            
        except Exception as e:
            print(f"❌ Error generando reporte: {e}")
            return "Error generando el reporte.", "error", 0.0

    def _procesar_carreras(self, user_message):
        """Procesar consultas sobre carreras"""
        try:
            carreras = self.get_carreras()
            
            respuesta = "🎓 **Carreras disponibles:**\n\n"
            for carrera in carreras:
                respuesta += f"• **{carrera['nombre']}** ({carrera['codigo']})\n"
                respuesta += f"  Duración: {carrera['duracion_semestres']} semestres\n"
                respuesta += f"  Inscripción: ${carrera['costo_inscripcion']}\n\n"
            
            return respuesta, "carreras", 0.9
            
        except Exception as e:
            print(f"❌ Error obteniendo carreras: {e}")
            return "Error obteniendo información de carreras.", "error", 0.0

    def _procesar_consulta_estudiantes(self, user_message):
        """Procesar consultas sobre estudiantes"""
        try:
            if 'total' in user_message:
                estadisticas = self.get_estadisticas_estudiantes()
                return f"👥 **Total de estudiantes registrados:** {estadisticas['total_estudiantes']}", "estudiantes_total", 0.9
            
            return "Puedo ayudarte con información de estudiantes. ¿Quieres saber el total, por carrera o pendientes de inscripción?", "estudiantes", 0.8
            
        except Exception as e:
            print(f"❌ Error procesando consulta estudiantes: {e}")
            return "Error obteniendo información de estudiantes.", "error", 0.0

    # === MÉTODOS UNIVERSITARIOS ===

    def get_estadisticas_estudiantes(self):
        """Obtener estadísticas generales de estudiantes"""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            # Total de estudiantes
            cur.execute('SELECT COUNT(*) as total FROM estudiantes')
            total_estudiantes = cur.fetchone()['total']
            
            # Estudiantes con inscripción pagada
            cur.execute('SELECT COUNT(*) as pagados FROM estudiantes WHERE inscripcion_pagada = TRUE')
            inscritos_pagados = cur.fetchone()['pagados']
            
            # Estudiantes que deben inscripción
            cur.execute('SELECT COUNT(*) as pendientes FROM estudiantes WHERE inscripcion_pagada = FALSE')
            pendientes_inscripcion = cur.fetchone()['pendientes']
            
            # Distribución por carrera
            cur.execute('''
                SELECT carrera, COUNT(*) as cantidad 
                FROM estudiantes 
                GROUP BY carrera 
                ORDER BY cantidad DESC
            ''')
            por_carrera = cur.fetchall()
            
            cur.close()
            conn.close()
            
            return {
                'total_estudiantes': total_estudiantes,
                'inscritos_pagados': inscritos_pagados,
                'pendientes_inscripcion': pendientes_inscripcion,
                'por_carrera': por_carrera
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return {}

    def get_estudiantes_pendientes_inscripcion(self):
        """Obtener lista de estudiantes que deben inscripción"""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            cur.execute('''
                SELECT matricula, nombre, apellido, carrera, semestre, fecha_inscripcion
                FROM estudiantes 
                WHERE inscripcion_pagada = FALSE
                ORDER BY fecha_inscripcion DESC
            ''')
            
            estudiantes = cur.fetchall()
            cur.close()
            conn.close()
            
            return estudiantes
            
        except Exception as e:
            print(f"❌ Error obteniendo estudiantes pendientes: {e}")
            return []

    def get_estudiantes_por_carrera(self, carrera=None):
        """Obtener estudiantes filtrados por carrera"""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            if carrera:
                cur.execute('''
                    SELECT matricula, nombre, apellido, semestre, inscripcion_pagada
                    FROM estudiantes 
                    WHERE carrera = %s
                    ORDER BY nombre
                ''', (carrera,))
            else:
                cur.execute('''
                    SELECT matricula, nombre, apellido, carrera, semestre, inscripcion_pagada
                    FROM estudiantes 
                    ORDER BY carrera, nombre
                ''')
            
            estudiantes = cur.fetchall()
            cur.close()
            conn.close()
            
            return estudiantes
            
        except Exception as e:
            print(f"❌ Error obteniendo estudiantes por carrera: {e}")
            return []

    def get_carreras(self):
        """Obtener lista de carreras"""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            cur.execute('SELECT codigo, nombre, duracion_semestres, costo_inscripcion FROM carreras WHERE activa = TRUE ORDER BY nombre')
            
            carreras = cur.fetchall()
            cur.close()
            conn.close()
            
            return carreras
            
        except Exception as e:
            print(f"❌ Error obteniendo carreras: {e}")
            return []

    def generar_reporte_inscripciones(self):
        """Generar reporte de inscripciones pendientes"""
        try:
            estudiantes_pendientes = self.get_estudiantes_pendientes_inscripcion()
            
            # Simular generación de archivo
            reporte_id = f"reporte_inscripciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            conn = self.get_connection()
            cur = conn.cursor()
            
            # Guardar metadata del reporte
            cur.execute('''
                INSERT INTO reportes_generados (tipo_reporte, parametros, generado_por)
                VALUES (%s, %s, %s)
            ''', ('inscripciones_pendientes', 
                 {'cantidad_estudiantes': len(estudiantes_pendientes)}, 
                 'sistema_chatbot'))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return {
                'reporte_id': reporte_id,
                'tipo': 'inscripciones_pendientes',
                'estudiantes': estudiantes_pendientes,
                'total_pendientes': len(estudiantes_pendientes),
                'fecha_generacion': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error generando reporte: {e}")
            return {}

    def buscar_estudiante(self, criterio, valor):
        """Buscar estudiante por diferentes criterios"""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            if criterio == 'matricula':
                cur.execute('SELECT * FROM estudiantes WHERE matricula = %s', (valor,))
            elif criterio == 'nombre':
                cur.execute('SELECT * FROM estudiantes WHERE nombre ILIKE %s OR apellido ILIKE %s', 
                           (f'%{valor}%', f'%{valor}%'))
            elif criterio == 'carrera':
                cur.execute('SELECT * FROM estudiantes WHERE carrera ILIKE %s', (f'%{valor}%',))
            else:
                return []
            
            estudiantes = cur.fetchall()
            cur.close()
            conn.close()
            
            return estudiantes
            
        except Exception as e:
            print(f"❌ Error buscando estudiante: {e}")
            return []

    # === MÉTODOS EXISTENTES DEL CHATBOT ===

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
        valuable_intents = {'services', 'contact', 'hours', 'location', 'pricing', 
                           'estadisticas_universidad', 'inscripciones_pendientes', 
                           'reporte_generado', 'carreras', 'estudiantes'}
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
                'top_intents': []
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo analytics: {e}")
            return {}