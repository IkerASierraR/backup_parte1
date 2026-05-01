"""
Rutas de restauración.
"""
from flask import Blueprint, request, jsonify
from application.restore_use_case import RestoreUseCase
from application.restore_backup_use_case import RestoreBackupUseCase

restore_bp = Blueprint('restore', __name__)


@restore_bp.route('/restore/execute', methods=['POST'])
def execute_restore():
    """Ejecuta una restauración."""
    try:
        data = request.get_json()
        server = data.get('server', '')
        database = data.get('database', '')
        username = data.get('username', '')
        password = data.get('password', '')
        backup_file = data.get('backup_file', '')
        
        if not all([server, database, username, password, backup_file]):
            return jsonify({
                "success": False,
                "message": "Todos los campos son requeridos"
            }), 400
        
        use_case = RestoreUseCase()
        result = use_case.execute_restore(
            server=server,
            database=database,
            username=username,
            password=password,
            backup_file=backup_file
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error en restauración: {str(e)}"
        }), 500


@restore_bp.route('/restore/list', methods=['POST'])
def list_backups():
    """Lista backups disponibles."""
    try:
        data = request.get_json()
        server = data.get('server', '')
        database = data.get('database', '')
        username = data.get('username', '')
        password = data.get('password', '')
        
        use_case = RestoreBackupUseCase()
        result = use_case.list_backups(
            server=server,
            database=database,
            username=username,
            password=password
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al listar backups: {str(e)}"
        }), 500