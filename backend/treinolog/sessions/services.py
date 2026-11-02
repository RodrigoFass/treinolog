from datetime import datetime

from werkzeug.exceptions import BadRequest, NotFound

from treinolog.auth.models import User
from treinolog.exercises.models import Exercise
from treinolog.ext.db import db
from treinolog.sessions.models import SetLog, WorkoutSession
from treinolog.utils import optional_str, to_datetime, to_float, to_int
from treinolog.workouts.models import Workout, WorkoutExercise
from treinolog.workouts.services import get_student


def _resolve_student(user: User, student_id: int | None) -> User:
    """Aluno consulta a si mesmo; personal consulta um dos seus alunos."""
    if user.role == "aluno":
        return user
    if student_id is None:
        raise BadRequest("Informe o parametro 'student_id'")
    return get_student(user, student_id)


# ==========================================================
# RF06: registrar a sessao de treino
# ==========================================================
def start_session(student: User, data: dict) -> WorkoutSession:
    workout = db.session.get(Workout, to_int(data, "workout_id", 1, 2**31 - 1))
    if workout is None or workout.student_id != student.id or not workout.is_active:
        raise NotFound("Ficha ativa nao encontrada")

    sets = data.get("sets") or []
    if not isinstance(sets, list):
        raise BadRequest("Campo 'sets' deve ser uma lista")

    session = WorkoutSession(
        workout=workout,
        student_id=student.id,
        performed_at=to_datetime(data, "performed_at") or datetime.now(),
        notes=optional_str(data, "notes"),
    )
    db.session.add(session)
    for set_data in sets:
        _upsert_set(session, set_data)

    db.session.commit()
    return session


def log_set(session: WorkoutSession, data: dict) -> SetLog:
    set_log = _upsert_set(session, data)
    db.session.commit()
    return set_log


def _upsert_set(session: WorkoutSession, data: dict) -> SetLog:
    if not isinstance(data, dict):
        raise BadRequest("Cada serie deve ser um objeto")

    item = db.session.get(WorkoutExercise, to_int(data, "workout_exercise_id", 1, 2**31 - 1))
    if item is None or item.workout_id != session.workout_id:
        raise BadRequest("Exercicio nao pertence a ficha desta sessao")

    set_number = to_int(data, "set_number", 1, item.sets)
    reps_done = to_int(data, "reps_done", 0, 255)
    load_kg = to_float(data, "load_kg", 0, 9999.99)

    # Uma linha por serie de cada exercicio na sessao: registrar de novo corrige o valor
    set_log = next(
        (
            s
            for s in session.set_logs
            if s.workout_exercise_id == item.id and s.set_number == set_number
        ),
        None,
    )
    if set_log is None:
        set_log = SetLog(workout_exercise=item, set_number=set_number)
        session.set_logs.append(set_log)

    set_log.reps_done = reps_done
    set_log.load_kg = load_kg
    return set_log


def update_session(session: WorkoutSession, data: dict) -> WorkoutSession:
    if "notes" in data:
        session.notes = optional_str(data, "notes")
    if "performed_at" in data:
        session.performed_at = to_datetime(data, "performed_at") or session.performed_at
    db.session.commit()
    return session


def delete_session(session: WorkoutSession) -> None:
    db.session.delete(session)
    db.session.commit()


# ==========================================================
# RF07: historico de sessoes por data
# ==========================================================
def list_sessions(user: User, student_id: int | None = None) -> list[WorkoutSession]:
    student = _resolve_student(user, student_id)
    return db.session.scalars(
        db.select(WorkoutSession)
        .filter_by(student_id=student.id)
        .order_by(WorkoutSession.performed_at.desc())
    ).all()


def get_session(user: User, session_id: int) -> WorkoutSession:
    session = db.session.get(WorkoutSession, session_id)
    if session is None:
        raise NotFound("Sessao nao encontrada")

    allowed = session.student_id == user.id or (
        user.role == "personal" and session.student.personal_id == user.id
    )
    if not allowed:
        raise NotFound("Sessao nao encontrada")
    return session


def get_own_session(student: User, session_id: int) -> WorkoutSession:
    session = get_session(student, session_id)
    if session.student_id != student.id:
        raise NotFound("Sessao nao encontrada")
    return session


# ==========================================================
# RF08: evolucao da carga maxima por exercicio
# ==========================================================
def trained_exercises(user: User, student_id: int | None = None) -> list[Exercise]:
    student = _resolve_student(user, student_id)
    return db.session.scalars(
        db.select(Exercise)
        .join(WorkoutExercise, WorkoutExercise.exercise_id == Exercise.id)
        .join(SetLog, SetLog.workout_exercise_id == WorkoutExercise.id)
        .join(WorkoutSession, WorkoutSession.id == SetLog.session_id)
        .where(WorkoutSession.student_id == student.id)
        .distinct()
        .order_by(Exercise.name)
    ).all()


def load_progress(user: User, exercise_id: int, student_id: int | None = None) -> list[dict]:
    student = _resolve_student(user, student_id)
    rows = db.session.execute(
        db.select(
            WorkoutSession.id,
            WorkoutSession.performed_at,
            db.func.max(SetLog.load_kg).label("max_load_kg"),
        )
        .join(SetLog, SetLog.session_id == WorkoutSession.id)
        .join(WorkoutExercise, WorkoutExercise.id == SetLog.workout_exercise_id)
        .where(
            WorkoutSession.student_id == student.id,
            WorkoutExercise.exercise_id == exercise_id,
        )
        .group_by(WorkoutSession.id, WorkoutSession.performed_at)
        .order_by(WorkoutSession.performed_at)
    ).all()

    return [
        {
            "session_id": row.id,
            "performed_at": row.performed_at.isoformat(),
            "max_load_kg": float(row.max_load_kg),
        }
        for row in rows
    ]
