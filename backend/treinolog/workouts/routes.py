from flask import Blueprint
from flask_jwt_extended import current_user, jwt_required

from treinolog.ext.jwt import role_required
from treinolog.utils import query_int, validate_json
from treinolog.workouts.schemas import (
    ItemUpdateSchema,
    PrescricaoSchema,
    WorkoutCreateSchema,
    WorkoutUpdateSchema,
)
from treinolog.workouts import services

bp = Blueprint("workouts", __name__)


# ==========================================================
# FICHAS
# ==========================================================
@bp.get("")
@jwt_required()
def list_workouts():
    workouts = services.list_workouts(current_user, query_int("student_id"))
    return {"workouts": [w.to_dict() for w in workouts]}


@bp.post("")
@role_required("personal")
def create_workout():
    workout = services.create_workout(current_user, validate_json(WorkoutCreateSchema))
    return workout.to_dict(), 201


@bp.get("/<int:workout_id>")
@jwt_required()
def get_workout(workout_id):
    return services.get_workout(current_user, workout_id).to_dict()


@bp.put("/<int:workout_id>")
@role_required("personal")
def update_workout(workout_id):
    workout = services.get_own_workout(current_user, workout_id)
    return services.update_workout(workout, validate_json(WorkoutUpdateSchema)).to_dict()


@bp.delete("/<int:workout_id>")
@role_required("personal")
def delete_workout(workout_id):
    services.delete_workout(services.get_own_workout(current_user, workout_id))
    return "", 204


# ==========================================================
# EXERCICIOS DA FICHA
# ==========================================================
@bp.post("/<int:workout_id>/exercises")
@role_required("personal")
def add_item(workout_id):
    workout = services.get_own_workout(current_user, workout_id)
    return services.add_item(workout, validate_json(PrescricaoSchema)).to_dict(), 201


@bp.put("/<int:workout_id>/exercises/<int:item_id>")
@role_required("personal")
def update_item(workout_id, item_id):
    workout = services.get_own_workout(current_user, workout_id)
    item = services.get_item(workout, item_id)
    return services.update_item(item, validate_json(ItemUpdateSchema)).to_dict()


@bp.delete("/<int:workout_id>/exercises/<int:item_id>")
@role_required("personal")
def delete_item(workout_id, item_id):
    workout = services.get_own_workout(current_user, workout_id)
    services.delete_item(services.get_item(workout, item_id))
    return "", 204
