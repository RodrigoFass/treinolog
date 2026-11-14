import logging

from werkzeug.exceptions import BadRequest, Conflict, Forbidden, NotFound

from treinolog.auth.models import User
from treinolog.exercises.models import Exercise
from treinolog.ext.db import db
from treinolog.sessions.models import SetLog, WorkoutSession
from treinolog.utils import optional_str, required_str, to_float, to_int
from treinolog.workouts.models import Workout, WorkoutExercise

logger = logging.getLogger(__name__)


# ==========================================================
# AUXILIARES
# ==========================================================
def get_student(personal: User, student_id: int) -> User:
    student = db.session.get(User, student_id)
    if student is None or student.role != "aluno" or student.personal_id != personal.id:
        raise NotFound("Aluno nao encontrado entre os seus alunos")
    return student


def _get_own_exercise(personal: User, exercise_id) -> Exercise:
    exercise = db.session.get(Exercise, exercise_id) if isinstance(exercise_id, int) else None
    if exercise is None or exercise.personal_id != personal.id:
        raise BadRequest("Exercicio invalido: use um exercicio do seu catalogo")
    return exercise


def _apply_prescription(item: WorkoutExercise, data: dict, partial: bool = False) -> None:
    """Valida e aplica series, repeticoes, carga sugerida e descanso."""
    if not partial or "sets" in data:
        item.sets = to_int(data, "sets", 1, 20)
    if not partial or "reps" in data:
        item.reps = required_str(data, "reps", 10)
    if not partial or "suggested_load_kg" in data:
        item.suggested_load_kg = to_float(data, "suggested_load_kg", 0, 9999.99, required=False)
    if not partial or "rest_seconds" in data:
        item.rest_seconds = to_int(data, "rest_seconds", 0, 3600, required=False)


def _next_position(workout: Workout) -> int:
    return max((item.position for item in workout.items), default=0) + 1


# ==========================================================
# RF04: montar ficha e atribuir ao aluno
# ==========================================================
def create_workout(personal: User, data: dict) -> Workout:
    student = get_student(personal, to_int(data, "student_id", 1, 2**31 - 1))
    exercises = data.get("exercises") or []
    if not isinstance(exercises, list):
        raise BadRequest("Campo 'exercises' deve ser uma lista")

    workout = Workout(
        personal_id=personal.id,
        student_id=student.id,
        name=required_str(data, "name", 60),
        notes=optional_str(data, "notes"),
    )
    for position, item_data in enumerate(exercises, start=1):
        if not isinstance(item_data, dict):
            raise BadRequest("Cada exercicio da ficha deve ser um objeto")
        item = WorkoutExercise(
            exercise=_get_own_exercise(personal, item_data.get("exercise_id")),
            position=position,
        )
        _apply_prescription(item, item_data)
        workout.items.append(item)

    db.session.add(workout)
    db.session.commit()
    logger.info(
        "Ficha id=%s criada pelo personal id=%s para o aluno id=%s",
        workout.id, personal.id, student.id,
    )
    return workout


def update_workout(workout: Workout, data: dict) -> Workout:
    if "name" in data:
        workout.name = required_str(data, "name", 60)
    if "notes" in data:
        workout.notes = optional_str(data, "notes")
    if "is_active" in data:
        if not isinstance(data["is_active"], bool):
            raise BadRequest("Campo 'is_active' deve ser verdadeiro ou falso")
        workout.is_active = data["is_active"]

    db.session.commit()
    return workout


def delete_workout(workout: Workout) -> None:
    has_sessions = db.session.scalar(db.select(WorkoutSession).filter_by(workout_id=workout.id))
    if has_sessions:
        raise Conflict("Ficha ja tem treinos registrados: desative-a para manter o historico")

    db.session.delete(workout)
    db.session.commit()
    logger.info("Ficha id=%s excluida", workout.id)


def add_item(workout: Workout, data: dict) -> WorkoutExercise:
    item = WorkoutExercise(
        exercise=_get_own_exercise(workout.personal, data.get("exercise_id")),
        position=_next_position(workout),
    )
    _apply_prescription(item, data)
    workout.items.append(item)
    db.session.commit()
    return item


def get_item(workout: Workout, item_id: int) -> WorkoutExercise:
    item = db.session.get(WorkoutExercise, item_id)
    if item is None or item.workout_id != workout.id:
        raise NotFound("Exercicio nao encontrado nesta ficha")
    return item


def update_item(item: WorkoutExercise, data: dict) -> WorkoutExercise:
    _apply_prescription(item, data, partial=True)
    db.session.commit()
    return item


def delete_item(item: WorkoutExercise) -> None:
    has_logs = db.session.scalar(db.select(SetLog).filter_by(workout_exercise_id=item.id))
    if has_logs:
        raise Conflict(
            "Exercicio ja tem series registradas: crie uma nova ficha para nao perder o historico"
        )

    db.session.delete(item)
    db.session.commit()


# ==========================================================
# RF05: consulta das fichas
# ==========================================================
def list_workouts(user: User, student_id: int | None = None) -> list[Workout]:
    query = db.select(Workout)
    if user.role == "personal":
        query = query.filter_by(personal_id=user.id)
        if student_id is not None:
            query = query.filter_by(student_id=get_student(user, student_id).id)
    else:
        # O aluno so ve as proprias fichas ativas
        query = query.filter_by(student_id=user.id, is_active=True)

    return db.session.scalars(query.order_by(Workout.is_active.desc(), Workout.name)).all()


def get_workout(user: User, workout_id: int) -> Workout:
    workout = db.session.get(Workout, workout_id)
    if workout is None or user.id not in (workout.personal_id, workout.student_id):
        raise NotFound("Ficha nao encontrada")
    return workout


def get_own_workout(personal: User, workout_id: int) -> Workout:
    workout = get_workout(personal, workout_id)
    if workout.personal_id != personal.id:
        raise Forbidden("Apenas o personal que criou a ficha pode altera-la")
    return workout
