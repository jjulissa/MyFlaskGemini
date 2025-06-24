# app/models.py 

from datetime import datetime
from app import db 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False) 
    password = db.Column(db.String(200), nullable=False)
    # otras columnas que tengas...

    # Relación con ChatMessage
    messages = db.relationship('ChatMessage', back_populates='user', lazy=True)


class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'user' o 'assistant'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', back_populates='messages')

    def __repr__(self):
        return f'<ChatMessage {self.id} {self.role} {self.timestamp}>'
