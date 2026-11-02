from flask import Blueprint, request
from flask_jwt_extended import current_user

from treinolog.exercises import services
from treinolog.ext.jwt import role_required
from treinolog.utils import get_json

bp = Blueprint("exercises", __name__)


@bp.get("")
@role_required("personal")
def list_exercises():
    exercises = services.list_exercises(current_user, request.args.get("muscle_group"))
    return {"exercises": [e.to_dict() for e in exercises]}


@bp.post("")
@role_required("personal")
def create_exercise():
    exercise = services.create_exercise(current_user, get_json())
    return exercise.to_dict(), 201


@bp.get("/<int:exercise_id>")
@role_required("personal")
def get_exercise(exercise_id):
    return services.get_exercise(current_user, exercise_id).to_dict()


@bp.put("/<int:exercise_id>")
@role_required("personal")
def update_exercise(exercise_id):
    exercise = services.get_exercise(current_user, exercise_id)
    return services.update_exercise(exercise, get_json()).to_dict()


@bp.delete("/<int:exercise_id>")
@role_required("personal")
def delete_exercise(exercise_id):
    services.delete_exercise(services.get_exercise(current_user, exercise_id))
    return "", 204
