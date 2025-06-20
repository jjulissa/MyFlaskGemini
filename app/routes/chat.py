# app/routes/chat.py 

from flask_jwt_extended import get_jwt_identity
from flask import Blueprint, request, jsonify
from datetime import datetime
from app.models import ChatMessage, db

@chat_bp.route('/send', methods=['POST'])
@jwt_required()
def send_message():
    data = request.get_json()
    content = data.get('content')
    user_id = get_jwt_identity()  # Asumiendo que guardas user.id en el token

    # Guardar mensaje del usuario
    user_msg = ChatMessage(
        user_id=user_id,
        role='user',
        content=content,
        timestamp=datetime.utcnow()
    )
    db.session.add(user_msg)
    db.session.commit()

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=content,
            timeout=10
        )
        answer = response.text

        # Guardar respuesta del asistente
        assistant_msg = ChatMessage(
            user_id=user_id,
            role='assistant',
            content=answer,
            timestamp=datetime.utcnow()
        )
        db.session.add(assistant_msg)
        db.session.commit()

        return jsonify({"response": answer})

    except genai_error.GenAIError:
        return jsonify({"error": "Error en el servicio de IA"}), 502
    except requests.exceptions.Timeout:
        return jsonify({"error": "Tiempo de espera agotado en el servicio de IA"}), 502
    except Exception:
        return jsonify({"error": "Error interno en el servidor"}), 500



@chat_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    user_id = get_jwt_identity()
    messages = ChatMessage.query.filter_by(user_id=user_id).order_by(ChatMessage.timestamp.asc()).all()
    result = [
        {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat()
        }
        for msg in messages
    ]
    return jsonify(result)

