"""Rutas de autenticación y conectividad."""
from flask import Blueprint, jsonify, request

from domain.entities import ConnectionConfig
from infrastructure.sql_server_repository import SqlServerRepository

auth_bp = Blueprint('auth', __name__)


def _response(success: bool, message: str, data=None, status_code: int = 200):
    payload = {"success": success, "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status_code


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json(silent=True) or {}
        server = (data.get('server') or '').strip()
        if not server:
            return _response(False, "El campo 'server' es obligatorio.", status_code=400)

        conn = ConnectionConfig(
            server=server,
            username=(data.get('username') or '').strip(),
            password=data.get('password') or '',
            database=(data.get('database') or 'master').strip() or 'master',
            use_windows_auth=bool(data.get('use_windows_auth', False)),
        )
        connected = SqlServerRepository().test_connection(conn)
        if not connected:
            return _response(False, 'No se pudo conectar al servidor SQL Server.', status_code=401)

        return _response(True, 'Conexión validada correctamente.')
    except Exception:
        return _response(False, 'Ocurrió un error interno al validar conexión.', status_code=500)


@auth_bp.route('/disconnect', methods=['POST'])
def disconnect():
    return _response(True, 'Sesión cerrada correctamente')
