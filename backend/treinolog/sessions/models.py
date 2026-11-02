from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from treinolog.ext.db import db

if TYPE_CHECKING:
    from treinolog.auth.models import User
    from treinolog.workouts.models import Workout, WorkoutExercise


# === WorkoutSession (cada vez que o aluno executa uma ficha) ===
class WorkoutSession(db.Model):
    __tablename__ = "workout_sessions"
    __table_args__ = (
        Index("ix_ws_student_date", "student_id", "performed_at"),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    workout_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False
    )
    student_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    performed_at: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False, server_default=db.func.now()
    )
    notes: Mapped[Optional[str]] = mapped_column(db.Text)

    # ------------------------------------------------------
    # FICHA / ALUNO
    # ------------------------------------------------------
    workout: Mapped["Workout"] = relationship("Workout")

    student: Mapped["User"] = relationship(
        "User",
        back_populates="sessions",
    )

    # ------------------------------------------------------
    # SERIES REGISTRADAS
    # ------------------------------------------------------
    set_logs: Mapped[List["SetLog"]] = relationship(
        "SetLog",
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # ======================================================
    # SERIALIZACAO
    # ======================================================
    def to_dict(self, with_sets: bool = True) -> dict:
        data = {
            "id": self.id,
            "workout_id": self.workout_id,
            "workout_name": self.workout.name,
            "student_id": self.student_id,
            "performed_at": self.performed_at.isoformat() if self.performed_at else None,
            "notes": self.notes,
        }
        if with_sets:
            data["sets"] = [
                log.to_dict()
                for log in sorted(
                    self.set_logs,
                    key=lambda s: (s.workout_exercise.position, s.set_number),
                )
            ]
        return data

    # ======================================================
    # REPRESENTACAO
    # ======================================================
    def __repr__(self) -> str:
        return (
            f"<WorkoutSession id={self.id} workout_id={self.workout_id} "
            f"student_id={self.student_id}>"
        )


# === SetLog (carga e repeticoes feitas em cada serie) ===
class SetLog(db.Model):
    __tablename__ = "set_logs"
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "workout_exercise_id",
            "set_number",
            name="uq_set_logs",
        ),
        CheckConstraint("load_kg >= 0", name="ck_set_logs_load"),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("workout_sessions.id", ondelete="CASCADE"), nullable=False
    )
    workout_exercise_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("workout_exercises.id", ondelete="CASCADE"), nullable=False
    )
    set_number: Mapped[int] = mapped_column(db.SmallInteger, nullable=False)
    reps_done: Mapped[int] = mapped_column(db.SmallInteger, nullable=False)
    load_kg: Mapped[float] = mapped_column(
        db.Numeric(6, 2, asdecimal=False), nullable=False, default=0
    )

    # ------------------------------------------------------
    # SESSAO / ITEM DA FICHA
    # ------------------------------------------------------
    session: Mapped["WorkoutSession"] = relationship(
        "WorkoutSession",
        back_populates="set_logs",
    )

    workout_exercise: Mapped["WorkoutExercise"] = relationship("WorkoutExercise")

    # ======================================================
    # SERIALIZACAO
    # ======================================================
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "workout_exercise_id": self.workout_exercise_id,
            "exercise_id": self.workout_exercise.exercise_id,
            "exercise_name": self.workout_exercise.exercise.name,
            "set_number": self.set_number,
            "reps_done": self.reps_done,
            "load_kg": self.load_kg,
        }

    # ======================================================
    # REPRESENTACAO
    # ======================================================
    def __repr__(self) -> str:
        return (
            f"<SetLog id={self.id} session_id={self.session_id} "
            f"set_number={self.set_number} load_kg={self.load_kg}>"
        )
