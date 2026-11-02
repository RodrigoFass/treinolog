from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from treinolog.ext.db import db

if TYPE_CHECKING:
    from treinolog.auth.models import User


# === Exercise (catalogo de exercicios do personal) ===
class Exercise(db.Model):
    __tablename__ = "exercises"
    __table_args__ = (
        UniqueConstraint(
            "personal_id",
            "name",
            name="uq_exercises_personal_name",
        ),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    personal_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(db.String(120), nullable=False)
    muscle_group: Mapped[str] = mapped_column(db.String(60), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(db.Text)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False, server_default=db.func.now()
    )

    # ------------------------------------------------------
    # PERSONAL
    # ------------------------------------------------------
    personal: Mapped["User"] = relationship(
        "User",
        back_populates="exercises",
    )

    # ======================================================
    # SERIALIZACAO
    # ======================================================
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "muscle_group": self.muscle_group,
            "description": self.description,
        }

    # ======================================================
    # REPRESENTACAO
    # ======================================================
    def __repr__(self) -> str:
        return f"<Exercise id={self.id} name='{self.name}'>"
