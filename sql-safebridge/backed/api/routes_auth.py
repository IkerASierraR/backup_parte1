"""
Rutas de autenticación.
"""
from flask import Blueprint, request, jsonify
from application.validation_use_case import ValidationUseCase

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """Autentica un usuario contra SQL Server."""
    try:
        data = request.get_json()
        server = data.get('server', '')
        database = data.get('database', '')
        username = data.get('username', '')
        password = data.get('password', '')
        
        if not all([server, database, username, password]):
            return jsonify({
                "success": False,
                "message": "Todos los campos son requeridos"
            }), 400
        
        use_case = ValidationUseCase()
        result = use_case.validate_connection(server, database, username, password)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error en autenticación: {str(e)}"
        }), 500


@auth_bp.route('/disconnect', methods=['POST'])
def disconnect():
    """Cierra la sesión actual."""
    return jsonify({
        "success": True,
        "message": "Sesión cerrada correctamente"
    })