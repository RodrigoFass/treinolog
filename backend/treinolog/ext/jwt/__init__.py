from functools import wraps

from flask_jwt_extended import JWTManager, current_user, verify_jwt_in_request
from werkzeug.exceptions import Forbidden

jwt = JWTManager()


def init_app(app):
    jwt.init_app(app)


@jwt.user_lookup_loader
def _load_user(_jwt_header, jwt_data):
    # Deixa o usuario do token disponivel em flask_jwt_extended.current_user
    from treinolog.auth.models import User
    from treinolog.ext.db import db

    return db.session.get(User, int(jwt_data["sub"]))


@jwt.user_lookup_error_loader
def _user_not_found(_jwt_header, _jwt_data):
    return {"erro": "Usuario do token nao existe mais"}, 401


@jwt.unauthorized_loader
def _missing_token(reason):
    return {"erro": "Token de acesso ausente"}, 401


@jwt.invalid_token_loader
def _invalid_token(reason):
    return {"erro": "Token de acesso invalido"}, 401


@jwt.expired_token_loader
def _expired_token(_jwt_header, _jwt_data):
    return {"erro": "Token de acesso expirado"}, 401


def role_required(*roles):
    """RNF03: exige token valido e um dos perfis informados."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            if current_user.role not in roles:
                raise Forbidden("Perfil sem permissao para esta acao")
            return fn(*args, **kwargs)

        return wrapper

    return decorator
