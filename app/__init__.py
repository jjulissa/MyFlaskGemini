# app/__init__.py 

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from .config import Config 
from flask_cors import CORS 
from dotenv import load_dotenv 
from .config import Config
load_dotenv() 

db = SQLAlchemy()
jwt = JWTManager()
ma = Marshmallow() 

import google.api_core.retry
retry_policy = google.api_core.retry.Retry(
    initial=1.0,
    maximum=10.0,
    multiplier=2,
    predicate=google.api_core.retry.if_exception_type(
        google.api_core.exceptions.ResourceExhausted
    )
)

def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(Config) 
    CORS(app)

    db.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)

    # Importar blueprints
    from app.routes.auth import auth_bp
    from app.routes.chat import chat_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")

    return app

