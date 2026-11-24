import logging
from datetime import date, timedelta

from werkzeug.exceptions import BadRequest, Conflict, NotFound

from treinolog.auth.models import User
from treinolog.ext.db import db
from treinolog.nutrition.models import Meal, MealLog, MealPlan, WeightLog

logger = logging.getLogger(__name__)


# ==========================================================
# AUXILIARES
# ==========================================================
def get_patient(nutritionist: User, student_id: int) -> User:
    student = db.session.get(User, student_id)
    if (
        student is None
        or student.role != "aluno"
        or student.nutritionist_id != nutritionist.id
    ):
        raise NotFound("Aluno nao encontrado entre os seus pacientes")
    return student


def _student_for(user: User, student_id: int | None) -> User:
    """Aluno ve os proprios dados; nutricionista ve os do paciente informado."""
    if user.role == "aluno":
        return user
    if student_id is None:
        raise BadRequest("Informe o student_id do paciente")
    return get_patient(user, student_id)


def _day_or_today(day: str | None) -> date:
    value = date.fromisoformat(day) if day else date.today()
    if value > date.today():
        raise BadRequest("Nao da para registrar um dia que ainda nao chegou")
    return value


def _build_meals(plan: MealPlan, meals: list[dict]) -> None:
    for position, meal_data in enumerate(meals, start=1):
        plan.meals.append(Meal(position=position, **meal_data))


def _has_logs(plan: MealPlan) -> bool:
    return bool(
        db.session.scalar(
            db.select(MealLog.id).join(Meal).where(Meal.plan_id == plan.id).limit(1)
        )
    )


def active_plan(student: User) -> MealPlan | None:
    return db.session.scalar(
        db.select(MealPlan)
        .filter_by(student_id=student.id, is_active=True)
        .order_by(MealPlan.updated_at.desc())
    )


# ==========================================================
# RF11: plano alimentar (o nutricionista monta, o aluno consulta)
# ==========================================================
def create_plan(nutritionist: User, data: dict) -> MealPlan:
    student = get_patient(nutritionist, data["student_id"])

    # O aluno segue um plano por vez: o anterior e desativado, mas o historico fica.
    for old in db.session.scalars(
        db.select(MealPlan).filter_by(student_id=student.id, is_active=True)
    ):
        old.is_active = False

    plan = MealPlan(
        nutritionist_id=nutritionist.id,
        student_id=student.id,
        name=data["name"],
        goal=data.get("goal"),
        notes=data.get("notes"),
    )
    _build_meals(plan, data["meals"])
    db.session.add(plan)
    db.session.commit()
    logger.info(
        "Plano alimentar id=%s criado pelo nutricionista id=%s para o aluno id=%s",
        plan.id, nutritionist.id, student.id,
    )
    return plan


def list_plans(user: User, student_id: int | None = None) -> list[MealPlan]:
    query = db.select(MealPlan)
    if user.role == "nutricionista":
        query = query.filter_by(nutritionist_id=user.id)
        if student_id is not None:
            query = query.filter_by(student_id=get_patient(user, student_id).id)
    else:
        query = query.filter_by(student_id=user.id, is_active=True)
    return list(db.session.scalars(query.order_by(MealPlan.is_active.desc(), MealPlan.id.desc())))


def get_plan(user: User, plan_id: int) -> MealPlan:
    plan = db.session.get(MealPlan, plan_id)
    allowed = plan is not None and (
        (user.role == "nutricionista" and plan.nutritionist_id == user.id)
        or (user.role == "aluno" and plan.student_id == user.id)
    )
    if not allowed:
        raise NotFound("Plano alimentar nao encontrado")
    return plan


def update_plan(plan: MealPlan, data: dict) -> MealPlan:
    for field in ("name", "goal", "notes"):
        if field in data:
            setattr(plan, field, data[field])
    if data.get("is_active") is True and not plan.is_active:
        for other in db.session.scalars(
            db.select(MealPlan).filter_by(student_id=plan.student_id, is_active=True)
        ):
            other.is_active = False
    if "is_active" in data:
        plan.is_active = data["is_active"]
    if "meals" in data:
        if _has_logs(plan):
            raise Conflict(
                "O aluno ja registrou refeicoes deste plano: "
                "crie um novo plano para nao perder o historico"
            )
        plan.meals.clear()
        db.session.flush()
        _build_meals(plan, data["meals"])

    db.session.commit()
    logger.info("Plano alimentar id=%s atualizado", plan.id)
    return plan


def delete_plan(plan: MealPlan) -> None:
    if _has_logs(plan):
        raise Conflict(
            "O aluno ja registrou refeicoes deste plano: desative-o para manter o historico"
        )
    db.session.delete(plan)
    db.session.commit()
    logger.info("Plano alimentar id=%s excluido", plan.id)


# ==========================================================
# RF12: refeicoes do dia (o aluno marca o que comeu)
# ==========================================================
def day_summary(student: User, day: str | None = None) -> dict:
    when = _day_or_today(day)
    plan = active_plan(student)
    if plan is None:
        return {"day": when.isoformat(), "plan": None, "meals": [], "done": 0, "total": 0}

    done_ids = set(
        db.session.scalars(
            db.select(MealLog.meal_id).filter_by(student_id=student.id, day=when)
        )
    )
    meals = [{**meal.to_dict(), "done": meal.id in done_ids} for meal in plan.meals]
    return {
        "day": when.isoformat(),
        "plan": plan.to_dict(with_meals=False),
        "meals": meals,
        "done": sum(1 for meal in meals if meal["done"]),
        "total": len(meals),
        "kcal_done": sum(meal["kcal"] or 0 for meal in meals if meal["done"]),
    }


def check_meal(student: User, meal_id: int, data: dict) -> dict:
    meal = db.session.get(Meal, meal_id)
    if meal is None or meal.plan.student_id != student.id or not meal.plan.is_active:
        raise NotFound("Refeicao nao encontrada no seu plano")

    when = _day_or_today(data.get("day"))
    log = db.session.scalar(
        db.select(MealLog).filter_by(student_id=student.id, meal_id=meal.id, day=when)
    )
    if data["done"] and log is None:
        db.session.add(MealLog(student_id=student.id, meal_id=meal.id, day=when))
    elif not data["done"] and log is not None:
        db.session.delete(log)
    db.session.commit()
    return day_summary(student, when.isoformat())


def adherence(user: User, student_id: int | None, days: int = 14) -> list[dict]:
    """Quantas refeicoes do plano ativo o aluno marcou em cada um dos ultimos dias."""
    student = _student_for(user, student_id)
    plan = active_plan(student)
    total = len(plan.meals) if plan else 0
    start = date.today() - timedelta(days=days - 1)

    counts = dict(
        db.session.execute(
            db.select(MealLog.day, db.func.count(MealLog.id))
            .where(MealLog.student_id == student.id, MealLog.day >= start)
            .group_by(MealLog.day)
        ).all()
    )
    result = []
    for offset in range(days):
        day = start + timedelta(days=offset)
        done = min(counts.get(day, 0), total)
        result.append({
            "day": day.isoformat(),
            "done": done,
            "total": total,
            "percent": round(100 * done / total) if total else 0,
        })
    return result


# ==========================================================
# RF13: peso do aluno (um registro por dia)
# ==========================================================
def save_weight(student: User, data: dict) -> WeightLog:
    when = _day_or_today(data.get("day"))
    log = db.session.scalar(db.select(WeightLog).filter_by(student_id=student.id, day=when))
    if log is None:
        log = WeightLog(student_id=student.id, day=when, weight_kg=data["weight_kg"])
        db.session.add(log)
    else:
        log.weight_kg = data["weight_kg"]
    db.session.commit()
    logger.info("Peso registrado pelo aluno id=%s", student.id)
    return log


def list_weights(user: User, student_id: int | None) -> list[WeightLog]:
    student = _student_for(user, student_id)
    return list(
        db.session.scalars(
            db.select(WeightLog).filter_by(student_id=student.id).order_by(WeightLog.day)
        )
    )


# ==========================================================
# RF14: pacientes do nutricionista com o resumo de cada um
# ==========================================================
def list_patients(nutritionist: User) -> list[dict]:
    patients = db.session.scalars(
        db.select(User)
        .where(User.nutritionist_id == nutritionist.id, User.role == "aluno")
        .order_by(User.name)
    ).all()

    result = []
    for student in patients:
        last_weight = db.session.scalar(
            db.select(WeightLog).filter_by(student_id=student.id).order_by(WeightLog.day.desc())
        )
        week = adherence(nutritionist, student.id, days=7)
        planned = sum(d["total"] for d in week)
        plan = active_plan(student)
        result.append({
            **student.to_dict(),
            "plan_name": plan.name if plan else None,
            "last_weight": last_weight.to_dict() if last_weight else None,
            "adherence_7d": (
                round(100 * sum(d["done"] for d in week) / planned) if planned else None
            ),
        })
    return result
