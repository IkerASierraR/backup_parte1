"""
Configuración principal del servidor Flask.
"""
from flask import Flask
from flask_cors import CORS


def create_app():
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__)
    CORS(app)  # Permitir peticiones desde Electron
    
    # Registrar rutas
    from api.routes_auth import auth_bp
    from api.routes_backup import backup_bp
    from api.routes_restore import restore_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(backup_bp, url_prefix='/api')
    app.register_blueprint(restore_bp, url_prefix='/api')
    
    # Ruta de health check
    @app.route('/api/status')
    def status():
        return {"status": "online", "service": "SQL-SafeBridge API"}
    
    return app