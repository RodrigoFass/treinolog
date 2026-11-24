from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from treinolog.ext.db import db

if TYPE_CHECKING:
    from treinolog.exercises.models import Exercise
    from treinolog.sessions.models import WorkoutSession

ROLES = ("personal", "aluno", "nutricionista")
PROFISSIONAIS = ("personal", "nutricionista")


# === User (personais, nutricionistas e alunos) ===
class User(db.Model):
    __tablename__ = "users"

    # ======================================================
    # IDENTIFICACAO
    # ======================================================
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)

    # ======================================================
    # DADOS PRINCIPAIS
    # ======================================================
    name: Mapped[str] = mapped_column(db.String(120), nullable=False)
    email: Mapped[str] = mapped_column(db.String(160), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(db.String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        db.Enum(*ROLES, name="user_role", create_constraint=True), nullable=False
    )

    # ======================================================
    # VINCULO ALUNO -> PERSONAL E ALUNO -> NUTRICIONISTA
    # ======================================================
    invite_code: Mapped[Optional[str]] = mapped_column(db.String(8), unique=True)
    personal_id: Mapped[Optional[int]] = mapped_column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL")
    )
    nutritionist_id: Mapped[Optional[int]] = mapped_column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL", name="fk_users_nutritionist_id")
    )

    # ======================================================
    # AUDITORIA
    # ======================================================
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False, server_default=db.func.now()
    )

    # ------------------------------------------------------
    # PERSONAL / ALUNOS (auto-relacionamento)
    # ------------------------------------------------------
    personal: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="students",
        remote_side=[id],
        foreign_keys=[personal_id],
    )

    students: Mapped[List["User"]] = relationship(
        "User",
        back_populates="personal",
        foreign_keys=[personal_id],
    )

    # ------------------------------------------------------
    # NUTRICIONISTA / PACIENTES (auto-relacionamento)
    # ------------------------------------------------------
    nutritionist: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="patients",
        remote_side=[id],
        foreign_keys=[nutritionist_id],
    )

    patients: Mapped[List["User"]] = relationship(
        "User",
        back_populates="nutritionist",
        foreign_keys=[nutritionist_id],
    )

    # ------------------------------------------------------
    # CATALOGO DE EXERCICIOS (personal)
    # ------------------------------------------------------
    exercises: Mapped[List["Exercise"]] = relationship(
        "Exercise",
        back_populates="personal",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # ------------------------------------------------------
    # SESSOES REALIZADAS (aluno)
    # ------------------------------------------------------
    sessions: Mapped[List["WorkoutSession"]] = relationship(
        "WorkoutSession",
        back_populates="student",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # ======================================================
    # SENHA (RNF02: somente o hash e armazenado)
    # ======================================================
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    # ======================================================
    # SERIALIZACAO
    # ======================================================
    def to_dict(self) -> dict:
        data = {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "personal_id": self.personal_id,
            "nutritionist_id": self.nutritionist_id,
        }
        if self.role in PROFISSIONAIS:
            data["invite_code"] = self.invite_code
        return data

    # ======================================================
    # REPRESENTACAO
    # ======================================================
    def __repr__(self) -> str:
        return f"<User id={self.id} email='{self.email}' role='{self.role}'>"
