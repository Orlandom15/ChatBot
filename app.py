from flask import Flask, render_template, request, jsonify
import uuid
from datetime import datetime
from config.database import NeonDatabase

app = Flask(__name__)
db = NeonDatabase()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not user_message:
            return jsonify({'success': False, 'error': 'Mensaje vacío'})
        
        print(f"💬 Mensaje: '{user_message}' - Sesión: {session_id}")
        
        # Obtener respuesta del bot
        bot_response, intent, confidence = db.get_bot_response(user_message)
        
        # Preparar respuesta base
        response_data = {
            'success': True,
            'bot_response': bot_response,
            'intent': intent,
            'confidence': confidence
        }
        
        # 🔥 AGREGAR DATOS ESTRUCTURADOS SEGÚN EL TIPO DE CONSULTA
        user_lower = user_message.lower()
        
        # Consulta de estadísticas
        if any(palabra in user_lower for palabra in ['estadística', 'estadisticas', 'estadistica', 'total', 'cuántos', 'cuantos']):
            print("📊 Obteniendo estadísticas universitarias...")
            estadisticas = db.get_estadisticas_estudiantes()
            response_data['estadisticas'] = estadisticas
            print(f"✅ Estadísticas obtenidas: {estadisticas}")
        
        # Consulta de estudiantes pendientes
        elif any(palabra in user_lower for palabra in ['pendiente', 'pendientes', 'debe', 'inscripción', 'inscripcion', 'pago']):
            print("📋 Obteniendo estudiantes pendientes...")
            estudiantes = db.get_estudiantes_pendientes_inscripcion()
            response_data['estudiantes'] = estudiantes
            print(f"✅ Estudiantes pendientes obtenidos: {len(estudiantes)}")
        
        # Consulta de carreras
        elif any(palabra in user_lower for palabra in ['carrera', 'carreras', 'ingeniería', 'sistemas', 'industrial']):
            print("🎓 Obteniendo carreras...")
            carreras = db.get_carreras()
            response_data['carreras'] = carreras
            print(f"✅ Carreras obtenidas: {len(carreras)}")
        
        # Consulta de reportes
        elif any(palabra in user_lower for palabra in ['reporte', 'archivo', 'descargar', 'generar']):
            print("📄 Generando reporte...")
            reporte = db.generar_reporte_inscripciones()
            response_data['reporte'] = reporte
            print(f"✅ Reporte generado: {reporte.get('reporte_id', 'N/A')}")
        
        # Guardar conversación
        if session_id:
            db.save_conversation(
                session_id=session_id,
                user_message=user_message,
                bot_response=bot_response,
                intent=intent,
                confidence=confidence
            )
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Error en /chat: {e}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': 'Error interno',
            'bot_response': 'Lo siento, hubo un error. Por favor intenta nuevamente.'
        })

@app.route('/history')
def get_history():
    try:
        session_id = request.args.get('session_id')
        
        if not session_id:
            return jsonify({'success': True, 'history': []})
        
        chat_history = db.get_chat_history(session_id, limit=20)
        
        formatted_history = []
        for msg in chat_history:
            formatted_history.append({
                'type': msg['message_type'],
                'message': msg['user_message'] if msg['message_type'] == 'user' else msg['bot_response'],
                'timestamp': msg['created_at'].isoformat() if msg['created_at'] else datetime.now().isoformat()
            })
        
        return jsonify({
            'success': True,
            'history': formatted_history
        })
        
    except Exception as e:
        print(f"❌ Error en /history: {e}")
        return jsonify({'success': False, 'error': 'Error obteniendo historial'})

# 🔥 NUEVAS RUTAS PARA DATOS UNIVERSITARIOS
@app.route('/api/universidad/estadisticas')
def get_estadisticas_universidad():
    """Endpoint directo para obtener estadísticas"""
    try:
        estadisticas = db.get_estadisticas_estudiantes()
        return jsonify({
            'success': True,
            'estadisticas': estadisticas
        })
    except Exception as e:
        print(f"❌ Error en /api/universidad/estadisticas: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/universidad/estudiantes/pendientes')
def get_estudiantes_pendientes():
    """Endpoint directo para obtener estudiantes pendientes"""
    try:
        estudiantes = db.get_estudiantes_pendientes_inscripcion()
        return jsonify({
            'success': True,
            'estudiantes': estudiantes,
            'total': len(estudiantes)
        })
    except Exception as e:
        print(f"❌ Error en /api/universidad/estudiantes/pendientes: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/universidad/carreras')
def get_carreras_universidad():
    """Endpoint directo para obtener carreras"""
    try:
        carreras = db.get_carreras()
        return jsonify({
            'success': True,
            'carreras': carreras
        })
    except Exception as e:
        print(f"❌ Error en /api/universidad/carreras: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/universidad/estudiantes/todos')
def get_todos_estudiantes():
    """Endpoint directo para obtener TODOS los estudiantes"""
    try:
        limit = request.args.get('limit', 200, type=int)
        estudiantes = db.get_todos_estudiantes(limit)
        
        print(f"📊 Obtenidos {len(estudiantes)} estudiantes (todos)")
        
        return jsonify({
            'success': True,
            'estudiantes': estudiantes,
            'total': len(estudiantes),
            'limit': limit
        })
    except Exception as e:
        print(f"❌ Error en /api/universidad/estudiantes/todos: {e}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("🚀 ChatBot Universitario funcionando en http://localhost:5000")
    app.run(debug=True, port=5000)