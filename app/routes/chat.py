# app/routes/chat.py 

from google.ai import generativelanguage as genai
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.models import ChatMessage, db
import requests  # para capturar excepciones de timeout

# genai.configure(api_key="AIzaSyBsIVC1vdxxTGdp1GSdmr4Zqggqjpmy_HU")

chat_bp = Blueprint("chat", __name__)

@chat_bp.route('/send', methods=['POST'])
@jwt_required()
def send_message():
    data = request.get_json()
    content = data.get('content') 
    if not content:
        return jsonify({"error": "Mensaje vacío"}), 400
    user_id = get_jwt_identity()

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
        # Llamada correcta al método para chat completions
        response = genai.chat.completions.create(
            model="models/chat-bison-001",  # modelo oficial de Google (ajusta si quieres otro)
            messages=[{"role": "user", "content": content}],
            timeout=10
        )
        answer = response.choices[0].message['content']

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
        print("Petición recibida:", content)
        print("Usuario:", user_id)

    except requests.exceptions.Timeout:
        return jsonify({"error": "Tiempo de espera agotado en el servicio de IA"}), 502
    except Exception as e:
        print("Error en la IA:", e)
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


