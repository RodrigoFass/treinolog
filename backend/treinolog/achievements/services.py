from datetime import date, timedelta

from werkzeug.exceptions import BadRequest, NotFound

from treinolog.auth.models import User
from treinolog.ext.db import db
from treinolog.nutrition.models import Meal, MealLog, MealPlan
from treinolog.sessions.models import SetLog, WorkoutSession

# Meta de treinos por semana (domingo a sabado) para a semana contar como "sem falha"
WEEKLY_GOAL = 3

# Medalhas de tempo sem falha: (trilha, nivel, alvo)
#   treino: semanas seguidas batendo a meta de treinos
#   dieta: dias seguidos cumprindo todas as refeicoes do plano
MEDALS = [
    ("treino", "bronze", 1, "1 semana de treino sem falha"),
    ("treino", "prata", 4, "1 mês de treino sem falha"),
    ("treino", "ouro", 12, "3 meses de treino sem falha"),
    ("dieta", "bronze", 7, "7 dias de dieta sem falha"),
    ("dieta", "prata", 30, "30 dias de dieta sem falha"),
    ("dieta", "ouro", 90, "90 dias de dieta sem falha"),
]

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
    ("ofensiva-30", "Mês de ferro", "30 dias seguidos ativos",
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


def _week_start(day: date) -> date:
    """Domingo da semana do dia."""
    return day - timedelta(days=(day.weekday() + 1) % 7)


def _training_weeks(trained: set[date], today: date) -> tuple[int, int]:
    """Semanas seguidas batendo a meta de treinos: atual e recorde.
    A semana de hoje ainda esta em andamento: so conta se ja bateu a meta, e nao quebra."""
    per_week: dict[date, int] = {}
    for day in trained:
        week = _week_start(day)
        per_week[week] = per_week.get(week, 0) + 1
    good = {week for week, count in per_week.items() if count >= WEEKLY_GOAL}

    current = 0
    week = _week_start(today)
    if week not in good:
        week -= timedelta(days=7)
    while week in good:
        current += 1
        week -= timedelta(days=7)

    best = run = 0
    previous = None
    for week in sorted(good):
        run = run + 1 if previous and week - previous == timedelta(days=7) else 1
        best = max(best, run)
        previous = week
    return current, best


def _medals(training: tuple[int, int], diet: tuple[int, int]) -> list[dict]:
    values = {"treino": training, "dieta": diet}
    result = []
    for track, tier, target, title in MEDALS:
        current, best = values[track]
        result.append({
            "id": f"{track}-{tier}",
            "track": track,
            "tier": tier,
            "title": title,
            "target": target,
            "unit": "semanas" if track == "treino" else "dias",
            "progress": min(current, target),
            "unlocked": best >= target,
        })
    return result


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
    training = _training_weeks(trained, today)
    diet_run = _streaks(diet, today)

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
        "weekly_goal": WEEKLY_GOAL,
        "trained_this_week": sum(1 for d in trained if _week_start(d) == _week_start(today)),
        "training_weeks": {"current": training[0], "best": training[1]},
        "diet_streak": {"current": diet_run[0], "best": diet_run[1]},
        "medals": _medals(training, diet_run),
        "calendar": calendar,
        "badges": [
            {"id": badge_id, "title": title, "description": text, "unlocked": rule(stats)}
            for badge_id, title, text, rule in BADGES
        ],
    }
