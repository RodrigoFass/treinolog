from werkzeug.exceptions import Conflict, NotFound

from treinolog.auth.models import User
from treinolog.exercises.models import Exercise
from treinolog.ext.db import db
from treinolog.utils import optional_str, required_str
from treinolog.workouts.models import WorkoutExercise


def _ensure_unique_name(personal: User, name: str, exclude_id: int | None = None) -> None:
    query = db.select(Exercise).filter_by(personal_id=personal.id, name=name)
    if exclude_id is not None:
        query = query.where(Exercise.id != exclude_id)
    if db.session.scalar(query):
        raise Conflict("Ja existe um exercicio com esse nome no seu catalogo")


# ==========================================================
# RF03: catalogo de exercicios do personal
# ==========================================================
def list_exercises(personal: User, muscle_group: str | None = None) -> list[Exercise]:
    query = db.select(Exercise).filter_by(personal_id=personal.id)
    if muscle_group:
        query = query.filter_by(muscle_group=muscle_group)
    return db.session.scalars(query.order_by(Exercise.muscle_group, Exercise.name)).all()


def get_exercise(personal: User, exercise_id: int) -> Exercise:
    exercise = db.session.get(Exercise, exercise_id)
    # 404 tambem quando o exercicio e de outro personal, para nao expor dados alheios
    if exercise is None or exercise.personal_id != personal.id:
        raise NotFound("Exercicio nao encontrado")
    return exercise


def create_exercise(personal: User, data: dict) -> Exercise:
    name = required_str(data, "name", 120)
    _ensure_unique_name(personal, name)

    exercise = Exercise(
        personal_id=personal.id,
        name=name,
        muscle_group=required_str(data, "muscle_group", 60),
        description=optional_str(data, "description"),
    )
    db.session.add(exercise)
    db.session.commit()
    return exercise


def update_exercise(exercise: Exercise, data: dict) -> Exercise:
    if "name" in data:
        name = required_str(data, "name", 120)
        _ensure_unique_name(exercise.personal, name, exclude_id=exercise.id)
        exercise.name = name
    if "muscle_group" in data:
        exercise.muscle_group = required_str(data, "muscle_group", 60)
    if "description" in data:
        exercise.description = optional_str(data, "description")

    db.session.commit()
    return exercise


def delete_exercise(exercise: Exercise) -> None:
    # Regra do modelo fisico: um exercicio em uso numa ficha nao pode ser excluido
    in_use = db.session.scalar(db.select(WorkoutExercise).filter_by(exercise_id=exercise.id))
    if in_use:
        raise Conflict("Exercicio em uso em alguma ficha e nao pode ser excluido")

    db.session.delete(exercise)
    db.session.commit()
