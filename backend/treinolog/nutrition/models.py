from datetime import date, datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from treinolog.ext.db import db

if TYPE_CHECKING:
    from treinolog.auth.models import User


# === MealPlan (plano alimentar que o nutricionista monta para o aluno) ===
class MealPlan(db.Model):
    __tablename__ = "meal_plans"
    __table_args__ = (
        Index("ix_meal_plans_student_active", "student_id", "is_active"),
    )

    # ======================================================
    # IDENTIFICACAO
    # ======================================================
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)

    nutritionist_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    student_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # ======================================================
    # DADOS PRINCIPAIS
    # ======================================================
    name: Mapped[str] = mapped_column(db.String(60), nullable=False)
    goal: Mapped[Optional[str]] = mapped_column(db.String(120))
    notes: Mapped[Optional[str]] = mapped_column(db.Text)
    is_active: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=True)

    # ======================================================
    # AUDITORIA
    # ======================================================
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False, server_default=db.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now()
    )

    # ------------------------------------------------------
    # USUARIOS
    # ------------------------------------------------------
    nutritionist: Mapped["User"] = relationship("User", foreign_keys=[nutritionist_id])
    student: Mapped["User"] = relationship("User", foreign_keys=[student_id])

    # ------------------------------------------------------
    # REFEICOES DO PLANO
    # ------------------------------------------------------
    meals: Mapped[List["Meal"]] = relationship(
        "Meal",
        back_populates="plan",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Meal.position",
    )

    # ======================================================
    # SERIALIZACAO
    # ======================================================
    def to_dict(self, with_meals: bool = True) -> dict:
        data = {
            "id": self.id,
            "nutritionist_id": self.nutritionist_id,
            "student_id": self.student_id,
            "name": self.name,
            "goal": self.goal,
            "notes": self.notes,
            "is_active": self.is_active,
            "total_kcal": sum(meal.kcal or 0 for meal in self.meals),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if with_meals:
            data["meals"] = [meal.to_dict() for meal in self.meals]
        return data

    def __repr__(self) -> str:
        return f"<MealPlan id={self.id} name='{self.name}' student_id={self.student_id}>"


# === Meal (refeicao do plano: cafe da manha, almoco...) ===
class Meal(db.Model):
    __tablename__ = "meals"
    __table_args__ = (
        UniqueConstraint("plan_id", "position", name="uq_meals_plan_position"),
        CheckConstraint("kcal IS NULL OR kcal BETWEEN 0 AND 5000", name="ck_meals_kcal"),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    plan_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("meal_plans.id", ondelete="CASCADE"), nullable=False
    )
    position: Mapped[int] = mapped_column(db.SmallInteger, nullable=False)
    name: Mapped[str] = mapped_column(db.String(60), nullable=False)
    time: Mapped[Optional[str]] = mapped_column(db.String(5))  # "07:30"
    foods: Mapped[str] = mapped_column(db.Text, nullable=False)
    kcal: Mapped[Optional[int]] = mapped_column(db.SmallInteger)

    plan: Mapped["MealPlan"] = relationship("MealPlan", back_populates="meals")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "position": self.position,
            "name": self.name,
            "time": self.time,
            "foods": self.foods,
            "kcal": self.kcal,
        }

    def __repr__(self) -> str:
        return f"<Meal id={self.id} plan_id={self.plan_id} name='{self.name}'>"


# === MealLog (aluno marcou que fez a refeicao naquele dia) ===
class MealLog(db.Model):
    __tablename__ = "meal_logs"
    __table_args__ = (
        UniqueConstraint("student_id", "meal_id", "day", name="uq_meal_logs_student_meal_day"),
        Index("ix_meal_logs_student_day", "student_id", "day"),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    meal_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("meals.id", ondelete="CASCADE"), nullable=False
    )
    day: Mapped[date] = mapped_column(db.Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False, server_default=db.func.now()
    )

    meal: Mapped["Meal"] = relationship("Meal")


# === WeightLog (peso do aluno, um registro por dia) ===
class WeightLog(db.Model):
    __tablename__ = "weight_logs"
    __table_args__ = (
        UniqueConstraint("student_id", "day", name="uq_weight_logs_student_day"),
        CheckConstraint("weight_kg > 0 AND weight_kg < 400", name="ck_weight_logs_weight"),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    day: Mapped[date] = mapped_column(db.Date, nullable=False)
    weight_kg: Mapped[float] = mapped_column(db.Numeric(5, 2, asdecimal=False), nullable=False)

    def to_dict(self) -> dict:
        return {"id": self.id, "day": self.day.isoformat(), "weight_kg": self.weight_kg}
