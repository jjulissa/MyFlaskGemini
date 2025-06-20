# app/routes/auth.py 

from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    # tu código de registro aquí
    return "Register endpoint"
 
