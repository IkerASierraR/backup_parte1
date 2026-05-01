"""Rutas de restauración."""
import os
from flask import Blueprint, jsonify, request

from application.restore_backup_use_case import RestoreBackupUseCase
from domain.entities import ConnectionConfig, OperationStatus
from infrastructure.sql_server_repository import SqlServerRepository
from shared.logger import UILogger, build_session_id

restore_bp = Blueprint("restore", __name__)


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
        database="master",
        use_windows_auth=bool(payload.get("use_windows_auth", False)),
    )


@restore_bp.route('/restore/execute', methods=['POST'])
def execute_restore():
    try:
        data = request.get_json(silent=True) or {}
        conn = _build_connection(data)
        backup_file = (data.get("backup_file") or "").strip()
        target_database = (data.get("target_database") or "").strip() or None
        force = bool(data.get("force", False))
        data_directory = (data.get("data_directory") or "").strip()
        log_directory = (data.get("log_directory") or "").strip()

        if not conn.server or not backup_file:
            return _response(False, "Los campos 'server' y 'backup_file' son obligatorios.", status_code=400)

        repo = SqlServerRepository()
        if not data_directory:
            data_directory = repo.get_default_backup_path(conn)
        if not log_directory:
            log_directory = data_directory

        logger = UILogger(build_session_id(target_database or "restore"))
        result = RestoreBackupUseCase(repo, logger).execute(
            config=conn,
            backup_file=backup_file,
            data_directory=data_directory,
            log_directory=log_directory,
            target_database=target_database,
            force=force,
        )
        logger.save_json()

        success = result.status == OperationStatus.SUCCESS
        blocked = result.status == OperationStatus.CANCELLED
        status_code = 409 if blocked else (200 if success else 400)
        message = "Restore completado correctamente." if success else (result.error_message or "No se pudo restaurar el backup.")

        return _response(success, message, {
            "backup_file": backup_file,
            "sandbox_database": result.sandbox_database,
            "status": result.status.value,
            "duration_seconds": result.duration_seconds,
        }, status_code=status_code)
    except Exception:
        return _response(False, "Ocurrió un error interno al ejecutar la restauración.", status_code=500)


@restore_bp.route('/restore/list', methods=['POST'])
def list_backups():
    try:
        data = request.get_json(silent=True) or {}
        backup_directory = (data.get("backup_directory") or "").strip()
        if not backup_directory:
            return _response(False, "El campo 'backup_directory' es obligatorio.", status_code=400)
        if not os.path.isdir(backup_directory):
            return _response(False, "El directorio de backups no existe.", status_code=404)

        backups = []
        for name in sorted(os.listdir(backup_directory), reverse=True):
            if not name.lower().endswith(".bak"):
                continue
            path = os.path.join(backup_directory, name)
            stat = os.stat(path)
            backups.append({
                "name": name,
                "path": path,
                "date": str(stat.st_mtime),
                "size": f"{round(stat.st_size / (1024 * 1024), 2)} MB",
                "status": "success",
            })

        return _response(True, "Backups listados correctamente.", {"backups": backups})
    except Exception:
        return _response(False, "Ocurrió un error interno al listar backups.", status_code=500)
