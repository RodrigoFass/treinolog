import re
import secrets
import string

from werkzeug.exceptions import BadRequest, Conflict, NotFound, Unauthorized

from treinolog.auth.models import ROLES, User
from treinolog.ext.db import db
from treinolog.sessions.models import WorkoutSession

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
INVITE_ALPHABET = string.ascii_uppercase + string.digits


def _new_invite_code() -> str:
    while True:
        code = "".join(secrets.choice(INVITE_ALPHABET) for _ in range(8))
        if not db.session.scalar(db.select(User).filter_by(invite_code=code)):
            return code


# ==========================================================
# RF01: cadastro e login
# ==========================================================
def register_user(name: str, email: str, password: str, role: str) -> User:
    email = email.strip().lower()
    if not EMAIL_RE.match(email):
        raise BadRequest("E-mail invalido")
    if len(password) < 6:
        raise BadRequest("A senha deve ter pelo menos 6 caracteres")
    if role not in ROLES:
        raise BadRequest("Perfil deve ser 'personal' ou 'aluno'")
    if db.session.scalar(db.select(User).filter_by(email=email)):
        raise Conflict("E-mail ja cadastrado")

    user = User(name=name, email=email, role=role)
    user.set_password(password)
    if role == "personal":
        user.invite_code = _new_invite_code()

    db.session.add(user)
    db.session.commit()
    return user


def authenticate(email: str, password: str) -> User:
    user = db.session.scalar(db.select(User).filter_by(email=email.strip().lower()))
    if user is None or not user.check_password(password):
        raise Unauthorized("E-mail ou senha incorretos")
    return user


# ==========================================================
# RF02: vinculo do aluno ao personal por codigo de convite
# ==========================================================
def link_student(student: User, invite_code: str) -> User:
    personal = db.session.scalar(
        db.select(User).filter_by(invite_code=invite_code.strip().upper(), role="personal")
    )
    if personal is None:
        raise NotFound("Codigo de convite nao encontrado")

    student.personal_id = personal.id
    db.session.commit()
    return personal


# ==========================================================
# RF09: alunos do personal com a data do ultimo treino
# ==========================================================
def list_students(personal: User) -> list[dict]:
    last_session = (
        db.select(
            WorkoutSession.student_id,
            db.func.max(WorkoutSession.performed_at).label("last_workout_at"),
        )
        .group_by(WorkoutSession.student_id)
        .subquery()
    )
    rows = db.session.execute(
        db.select(User, last_session.c.last_workout_at)
        .outerjoin(last_session, last_session.c.student_id == User.id)
        .where(User.personal_id == personal.id, User.role == "aluno")
        .order_by(User.name)
    ).all()

    return [
        {
            **student.to_dict(),
            "last_workout_at": last.isoformat() if last else None,
        }
        for student, last in rows
    ]
