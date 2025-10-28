from flask import Flask, render_template, request, jsonify
import uuid
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
        session_id = data.get('session_id')  # El frontend lo envía
        
        if not user_message:
            return jsonify({'success': False, 'error': 'Mensaje vacío'})
        
        print(f"💬 Mensaje: '{user_message}' - Sesión: {session_id}")
        
        # Obtener respuesta del bot
        bot_response, intent, confidence = db.get_bot_response(user_message)
        
        # Guardar conversación (session_id viene del frontend)
        if session_id:
            db.save_conversation(
                session_id=session_id,
                user_message=user_message,
                bot_response=bot_response,
                intent=intent,
                confidence=confidence
            )
        
        return jsonify({
            'success': True,
            'bot_response': bot_response,
            'intent': intent,
            'confidence': confidence
        })
        
    except Exception as e:
        print(f"❌ Error en /chat: {e}")
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

if __name__ == '__main__':
    print("🚀 ChatBot funcionando en http://localhost:5000")
    app.run(debug=True, port=5000)