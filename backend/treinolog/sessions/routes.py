from flask import Blueprint
from flask_jwt_extended import current_user, jwt_required
from werkzeug.exceptions import BadRequest

from treinolog.ext.jwt import role_required
from treinolog.sessions import services
from treinolog.sessions.schemas import SerieSchema, SessionCreateSchema, SessionUpdateSchema
from treinolog.utils import query_int, validate_json

bp = Blueprint("sessions", __name__)


# ==========================================================
# SESSOES DE TREINO
# ==========================================================
@bp.get("")
@jwt_required()
def list_sessions():
    sessions = services.list_sessions(current_user, query_int("student_id"))
    return {"sessions": [s.to_dict(with_sets=False) for s in sessions]}


@bp.post("")
@role_required("aluno")
def start_session():
    session = services.start_session(current_user, validate_json(SessionCreateSchema))
    return session.to_dict(), 201


@bp.get("/<int:session_id>")
@jwt_required()
def get_session(session_id):
    return services.get_session(current_user, session_id).to_dict()


@bp.put("/<int:session_id>")
@role_required("aluno")
def update_session(session_id):
    session = services.get_own_session(current_user, session_id)
    return services.update_session(session, validate_json(SessionUpdateSchema)).to_dict()


@bp.delete("/<int:session_id>")
@role_required("aluno")
def delete_session(session_id):
    services.delete_session(services.get_own_session(current_user, session_id))
    return "", 204


@bp.put("/<int:session_id>/sets")
@role_required("aluno")
def log_set(session_id):
    session = services.get_own_session(current_user, session_id)
    return services.log_set(session, validate_json(SerieSchema)).to_dict()


# ==========================================================
# EVOLUCAO DE CARGA
# ==========================================================
@bp.get("/progress/exercises")
@jwt_required()
def trained_exercises():
    exercises = services.trained_exercises(current_user, query_int("student_id"))
    return {"exercises": [e.to_dict() for e in exercises]}


@bp.get("/progress")
@jwt_required()
def load_progress():
    exercise_id = query_int("exercise_id")
    if exercise_id is None:
        raise BadRequest("Informe o parametro 'exercise_id'")
    points = services.load_progress(current_user, exercise_id, query_int("student_id"))
    return {"exercise_id": exercise_id, "points": points}
