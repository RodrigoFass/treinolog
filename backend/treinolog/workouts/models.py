from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from treinolog.ext.db import db

if TYPE_CHECKING:
    from treinolog.auth.models import User
    from treinolog.exercises.models import Exercise


# === Workout (fichas: Treino A, B, C... de um aluno) ===
class Workout(db.Model):
    __tablename__ = "workouts"
    __table_args__ = (
        Index("ix_workouts_student_active", "student_id", "is_active"),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    personal_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    student_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(db.String(60), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(db.Text)
    is_active: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False, server_default=db.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now()
    )

    # ------------------------------------------------------
    # USUARIOS
    # ------------------------------------------------------
    personal: Mapped["User"] = relationship(
        "User",
        foreign_keys=[personal_id],
    )

    student: Mapped["User"] = relationship(
        "User",
        foreign_keys=[student_id],
    )

    # ------------------------------------------------------
    # EXERCICIOS DA FICHA
    # ------------------------------------------------------
    items: Mapped[List["WorkoutExercise"]] = relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="WorkoutExercise.position",
    )

    # ======================================================
    # SERIALIZACAO
    # ======================================================
    def to_dict(self, with_items: bool = True) -> dict:
        data = {
            "id": self.id,
            "personal_id": self.personal_id,
            "student_id": self.student_id,
            "name": self.name,
            "notes": self.notes,
            "is_active": self.is_active,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if with_items:
            data["exercises"] = [item.to_dict() for item in self.items]
        return data

    # ======================================================
    # REPRESENTACAO
    # ======================================================
    def __repr__(self) -> str:
        return f"<Workout id={self.id} name='{self.name}' student_id={self.student_id}>"


# === WorkoutExercise (exercicio da ficha + prescricao) ===
class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"
    __table_args__ = (
        UniqueConstraint("workout_id", "position", name="uq_workout_exercises_pos"),
        CheckConstraint("sets BETWEEN 1 AND 20", name="ck_workout_exercises_sets"),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    workout_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False
    )
    exercise_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("exercises.id", ondelete="RESTRICT"), nullable=False
    )
    position: Mapped[int] = mapped_column(db.SmallInteger, nullable=False)
    sets: Mapped[int] = mapped_column(db.SmallInteger, nullable=False)
    reps: Mapped[str] = mapped_column(db.String(10), nullable=False)
    suggested_load_kg: Mapped[Optional[float]] = mapped_column(db.Numeric(6, 2, asdecimal=False))
    rest_seconds: Mapped[Optional[int]] = mapped_column(db.SmallInteger)

    # ------------------------------------------------------
    # FICHA / EXERCICIO
    # ------------------------------------------------------
    workout: Mapped["Workout"] = relationship(
        "Workout",
        back_populates="items",
    )

    exercise: Mapped["Exercise"] = relationship("Exercise")

    # ======================================================
    # SERIALIZACAO
    # ======================================================
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "exercise_id": self.exercise_id,
            "exercise_name": self.exercise.name,
            "muscle_group": self.exercise.muscle_group,
            "position": self.position,
            "sets": self.sets,
            "reps": self.reps,
            "suggested_load_kg": self.suggested_load_kg,
            "rest_seconds": self.rest_seconds,
        }

    # ======================================================
    # REPRESENTACAO
    # ======================================================
    def __repr__(self) -> str:
        return (
            f"<WorkoutExercise id={self.id} workout_id={self.workout_id} "
            f"exercise_id={self.exercise_id} position={self.position}>"
        )
