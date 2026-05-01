"""
Rutas de backup.
"""
from flask import Blueprint, request, jsonify
from application.backup_use_case import BackupUseCase
from application.validation_use_case import ValidationUseCase

backup_bp = Blueprint('backup', __name__)


@backup_bp.route('/backup/execute', methods=['POST'])
def execute_backup():
    """Ejecuta un backup completo."""
    try:
        data = request.get_json()
        server = data.get('server', '')
        database = data.get('database', '')
        username = data.get('username', '')
        password = data.get('password', '')
        backup_type = data.get('backup_type', 'FULL')
        
        if not all([server, database, username, password]):
            return jsonify({
                "success": False,
                "message": "Faltan credenciales de conexión"
            }), 400
        
        use_case = BackupUseCase()
        result = use_case.execute_backup(
            server=server,
            database=database,
            username=username,
            password=password,
            backup_type=backup_type
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error en backup: {str(e)}"
        }), 500


@backup_bp.route('/backup/preview', methods=['POST'])
def preview_backup():
    """Previsualiza el backup sin ejecutarlo."""
    try:
        data = request.get_json()
        server = data.get('server', '')
        database = data.get('database', '')
        username = data.get('username', '')
        password = data.get('password', '')
        
        if not all([server, database, username, password]):
            return jsonify({
                "success": False,
                "message": "Faltan credenciales de conexión"
            }), 400
        
        use_case = BackupUseCase()
        result = use_case.preview_backup(
            server=server,
            database=database,
            username=username,
            password=password
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error en preview: {str(e)}"
        }), 500