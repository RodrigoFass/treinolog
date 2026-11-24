from datetime import date, timedelta

from werkzeug.exceptions import BadRequest, NotFound

from treinolog.auth.models import User
from treinolog.ext.db import db
from treinolog.nutrition.models import Meal, MealLog, MealPlan
from treinolog.sessions.models import SetLog, WorkoutSession

# Conquistas: (id, titulo, descricao, funcao que diz se desbloqueou)
BADGES = [
    ("primeiro-treino", "Primeiro treino", "Registrou o primeiro treino",
     lambda s: s["workouts"] >= 1),
    ("dez-treinos", "10 treinos", "Registrou 10 treinos",
     lambda s: s["workouts"] >= 10),
    ("ofensiva-3", "Ofensiva de 3 dias", "3 dias seguidos ativos",
     lambda s: s["best"] >= 3),
    ("ofensiva-7", "Semana completa", "7 dias seguidos ativos",
     lambda s: s["best"] >= 7),
    ("ofensiva-30", "Mes de ferro", "30 dias seguidos ativos",
     lambda s: s["best"] >= 30),
    ("dieta-7", "Dieta em dia", "Cumpriu o plano alimentar em 7 dias",
     lambda s: s["diet_days"] >= 7),
]


# ==========================================================
# AUXILIARES
# ==========================================================
def get_student(user: User, student_id: int | None) -> User:
    """Aluno ve a propria ofensiva; personal e nutricionista veem a dos seus alunos."""
    if user.role == "aluno":
        return user
    if student_id is None:
        raise BadRequest("Informe o student_id do aluno")
    student = db.session.get(User, student_id)
    linked = student is not None and student.role == "aluno" and (
        (user.role == "personal" and student.personal_id == user.id)
        or (user.role == "nutricionista" and student.nutritionist_id == user.id)
    )
    if not linked:
        raise NotFound("Aluno nao encontrado entre os seus alunos")
    return student


def _training_days(student: User) -> set[date]:
    """Dias com treino registrado (sessao com pelo menos uma serie feita)."""
    rows = db.session.scalars(
        db.select(WorkoutSession.performed_at)
        .join(SetLog, SetLog.session_id == WorkoutSession.id)
        .where(WorkoutSession.student_id == student.id)
        .distinct()
    )
    return {performed_at.date() for performed_at in rows}


def _diet_days(student: User) -> set[date]:
    """Dias em que o aluno marcou todas as refeicoes do plano que seguia."""
    rows = db.session.execute(
        db.select(MealLog.day, Meal.plan_id, db.func.count(MealLog.id))
        .join(Meal, Meal.id == MealLog.meal_id)
        .where(MealLog.student_id == student.id)
        .group_by(MealLog.day, Meal.plan_id)
    ).all()
    sizes = dict(
        db.session.execute(
            db.select(Meal.plan_id, db.func.count(Meal.id))
            .join(MealPlan, MealPlan.id == Meal.plan_id)
            .where(MealPlan.student_id == student.id)
            .group_by(Meal.plan_id)
        ).all()
    )
    return {day for day, plan_id, done in rows if done >= sizes.get(plan_id, 0) > 0}


def _streaks(active: set[date], today: date) -> tuple[int, int]:
    """Ofensiva atual e recorde. Hoje ainda sem atividade nao quebra a ofensiva."""
    current = 0
    day = today if today in active else today - timedelta(days=1)
    while day in active:
        current += 1
        day -= timedelta(days=1)

    best = run = 0
    previous = None
    for day in sorted(active):
        run = run + 1 if previous and day - previous == timedelta(days=1) else 1
        best = max(best, run)
        previous = day
    return current, best


# ==========================================================
# RF15: ofensiva, calendario de dias ativos e conquistas
# ==========================================================
def summary(user: User, student_id: int | None, weeks: int = 12) -> dict:
    student = get_student(user, student_id)
    today = date.today()
    trained = _training_days(student)
    diet = _diet_days(student)
    active = trained | diet
    current, best = _streaks(active, today)

    # Calendario: semanas completas (domingo a sabado), terminando na semana de hoje
    end = today + timedelta(days=(5 - today.weekday()) % 7)  # proximo sabado (ou hoje)
    start = end - timedelta(days=7 * weeks - 1)
    calendar = []
    for offset in range((end - start).days + 1):
        day = start + timedelta(days=offset)
        calendar.append({
            "day": day.isoformat(),
            "trained": day in trained,
            "diet": day in diet,
            "future": day > today,
        })

    stats = {
        "workouts": db.session.scalar(
            db.select(db.func.count(db.distinct(WorkoutSession.id)))
            .join(SetLog, SetLog.session_id == WorkoutSession.id)
            .where(WorkoutSession.student_id == student.id)
        ) or 0,
        "best": best,
        "diet_days": len(diet),
    }
    return {
        "student_id": student.id,
        "current_streak": current,
        "best_streak": best,
        "active_today": today in active,
        "active_days": len(active),
        "calendar": calendar,
        "badges": [
            {"id": badge_id, "title": title, "description": text, "unlocked": rule(stats)}
            for badge_id, title, text, rule in BADGES
        ],
    }
