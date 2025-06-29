# app/routes/chat.py

import os 
import traceback
import requests  # para capturar excepciones de timeout
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import ChatMessage, db
import google.generativeai as genai 
from google.api_core import retry as retries 
import google.api_core.exceptions

# Configurar API key de Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Crear Blueprint
chat_bp = Blueprint("chat", __name__) 

# Configurar política de reintentos
retry_policy = retries.Retry(
    initial=1.0,
    maximum=10.0,
    multiplier=2,
    predicate=retries.if_exception_type(
        google.api_core.exceptions.ResourceExhausted
    )
)

# Configurar API con política de reintentos
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)


# Ruta para enviar mensaje al asistente
@chat_bp.route('/send', methods=['POST'])
@jwt_required()
def send_message():
    try:
        data = request.get_json()
        content = data.get('content') or data.get('message')

        if not content:
            return jsonify({"error": "Mensaje vacío"}), 400

        user_id = get_jwt_identity()

        print("Petición recibida:", content)
        print("Usuario:", user_id)

        # Guardar mensaje del usuario
        user_msg = ChatMessage(
            user_id=user_id,
            role='user',
            content=content,
            timestamp=datetime.utcnow()
        )
        db.session.add(user_msg)
        db.session.commit()

        # Obtener respuesta de Gemini
        # model = genai.GenerativeModel("gemini-pro") 
        model = genai.GenerativeModel("gemini-1.5-flash")
        chat = model.start_chat()
        gemini_response = chat.send_message(content)
        answer = gemini_response.text

        print("Modelos disponibles:", [m.name for m in genai.list_models()])
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

    except requests.exceptions.Timeout:
        return jsonify({"error": "Tiempo de espera agotado en el servicio de IA"}), 502

    except Exception as e:
        print("Error en el servidor:")
        traceback.print_exc()
        return jsonify({
            "error": "Error interno en el servidor",
            "detalle": str(e)
        }), 500

# Ruta para recuperar historial del usuario
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



