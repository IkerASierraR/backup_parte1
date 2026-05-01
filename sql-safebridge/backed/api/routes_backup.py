"""Rutas de backup."""
from datetime import datetime
from flask import Blueprint, jsonify, request

from application.backup_use_case import BackupUseCase
from domain.entities import ConnectionConfig, OperationStatus
from infrastructure.sql_server_repository import SqlServerRepository
from shared.logger import UILogger, build_session_id

backup_bp = Blueprint("backup", __name__)


def _response(success: bool, message: str, data=None, status_code: int = 200):
    payload = {"success": success, "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status_code


def _build_connection(payload: dict) -> ConnectionConfig:
    return ConnectionConfig(
        server=payload.get("server", "").strip(),
        username=payload.get("username", "").strip(),
        password=payload.get("password", ""),
        database=payload.get("database", "master").strip() or "master",
        use_windows_auth=bool(payload.get("use_windows_auth", False)),
    )


@backup_bp.route('/backup/execute', methods=['POST'])
def execute_backup():
    """Ejecuta un backup de la base de datos indicada."""
    try:
        data = request.get_json(silent=True) or {}
        database = (data.get("database") or "").strip()
        backup_directory = (data.get("backup_directory") or "").strip()
        conn = _build_connection(data)

        if not conn.server or not database:
            return _response(False, "Los campos 'server' y 'database' son obligatorios.", status_code=400)

        if not backup_directory:
            repo = SqlServerRepository()
            backup_directory = repo.get_default_backup_path(conn)

        logger = UILogger(build_session_id(database))
        repo = SqlServerRepository()
        result = BackupUseCase(repo, logger).execute(
            config=conn,
            database_name=database,
            backup_directory=backup_directory,
        )
        logger.save_json()

        success = result.status == OperationStatus.SUCCESS
        code = 200 if success else 400
        return _response(
            success,
            "Backup completado correctamente." if success else (result.error_message or "No se pudo completar el backup."),
            {
                "database": database,
                "backup_path": result.backup_path,
                "status": result.status.value,
                "duration_seconds": result.duration_seconds,
                "file_size_mb": result.file_size_mb,
                "finished_at": result.finished_at.isoformat() if result.finished_at else datetime.now().isoformat(),
            },
            status_code=code,
        )
    except Exception:
        return _response(False, "Ocurrió un error interno al ejecutar el backup.", status_code=500)
