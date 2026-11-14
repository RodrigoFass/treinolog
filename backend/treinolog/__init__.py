import os

from flask import Flask

from .config import config
from .ext import cli, db, errors, jwt, logs


# ==========================================================
# APPLICATION FACTORY
# ==========================================================
def create_app(config_name=None):
    app = Flask(__name__)

    config_name = config_name or os.getenv("FLASK_CONFIG", "development")
    app.config.from_object(config.get(config_name, config["default"]))

    # ----------------------------------------------------------
    # Extensoes (logging primeiro, para registrar o resto)
    # ----------------------------------------------------------
    logs.init_app(app)
    app.logger.info(f"Aplicacao criada com config_name = {config_name}")

    db.init_app(app)
    db.register_models()
    jwt.init_app(app)
    errors.init_app(app)
    cli.init_app(app)

    # ----------------------------------------------------------
    # Blueprints (importados aqui dentro para evitar import circular)
    # ----------------------------------------------------------
    from . import auth, exercises, sessions, workouts

    auth.init_app(app)
    exercises.init_app(app)
    workouts.init_app(app)
    sessions.init_app(app)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app
