from flask import Blueprint, request
from flask_jwt_extended import current_user

from treinolog.ext.jwt import role_required
from treinolog.nutrition import services
from treinolog.nutrition.schemas import (
    MealCheckSchema,
    MealPlanCreateSchema,
    MealPlanUpdateSchema,
    WeightSchema,
)
from treinolog.utils import query_int, validate_json

bp = Blueprint("nutrition", __name__)


# ==========================================================
# PACIENTES (nutricionista)
# ==========================================================
@bp.get("/patients")
@role_required("nutricionista")
def patients():
    return {"patients": services.list_patients(current_user)}


# ==========================================================
# PLANOS ALIMENTARES
# ==========================================================
@bp.get("/plans")
@role_required("nutricionista", "aluno")
def list_plans():
    plans = services.list_plans(current_user, query_int("student_id"))
    return {"plans": [p.to_dict() for p in plans]}


@bp.post("/plans")
@role_required("nutricionista")
def create_plan():
    plan = services.create_plan(current_user, validate_json(MealPlanCreateSchema))
    return plan.to_dict(), 201


@bp.get("/plans/<int:plan_id>")
@role_required("nutricionista", "aluno")
def get_plan(plan_id):
    return services.get_plan(current_user, plan_id).to_dict()


@bp.put("/plans/<int:plan_id>")
@role_required("nutricionista")
def update_plan(plan_id):
    plan = services.get_plan(current_user, plan_id)
    return services.update_plan(plan, validate_json(MealPlanUpdateSchema)).to_dict()


@bp.delete("/plans/<int:plan_id>")
@role_required("nutricionista")
def delete_plan(plan_id):
    services.delete_plan(services.get_plan(current_user, plan_id))
    return "", 204


# ==========================================================
# REFEICOES DO DIA (aluno)
# ==========================================================
@bp.get("/today")
@role_required("aluno")
def today():
    return services.day_summary(current_user, request.args.get("day"))


@bp.put("/meals/<int:meal_id>/check")
@role_required("aluno")
def check_meal(meal_id):
    return services.check_meal(current_user, meal_id, validate_json(MealCheckSchema))


@bp.get("/adherence")
@role_required("nutricionista", "aluno")
def adherence():
    days = query_int("days") or 14
    return {"days": services.adherence(current_user, query_int("student_id"), min(days, 60))}


# ==========================================================
# PESO
# ==========================================================
@bp.get("/weights")
@role_required("nutricionista", "aluno")
def list_weights():
    weights = services.list_weights(current_user, query_int("student_id"))
    return {"weights": [w.to_dict() for w in weights]}


@bp.post("/weights")
@role_required("aluno")
def save_weight():
    return services.save_weight(current_user, validate_json(WeightSchema)).to_dict(), 201
