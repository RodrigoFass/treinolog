from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()
migrate = Migrate()


def init_app(app):
    db.init_app(app)
    migrate.init_app(app, db)


def register_models():
    """
    Importa todos os modulos que definem modelos para que
    sejam registrados no metadata do SQLAlchemy.
    """
    import treinolog.auth.models  # noqa: F401
    import treinolog.exercises.models  # noqa: F401
    import treinolog.workouts.models  # noqa: F401
    import treinolog.sessions.models  # noqa: F401


@event.listens_for(Engine, "connect")
def _sqlite_foreign_keys(dbapi_connection, connection_record):
    # O SQLite so respeita ON DELETE CASCADE/RESTRICT com essa pragma ligada.
    # No MySQL (InnoDB) as chaves estrangeiras ja sao verificadas.
    if dbapi_connection.__class__.__module__.startswith("sqlite3"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
