from flask import Blueprint
from flask_jwt_extended import create_access_token, current_user, jwt_required

from treinolog.auth import services
from treinolog.ext.jwt import role_required
from treinolog.utils import get_json, required_str

bp = Blueprint("auth", __name__)


@bp.post("/register")
def register():
    data = get_json()
    user = services.register_user(
        name=required_str(data, "name", 120),
        email=required_str(data, "email", 160),
        password=required_str(data, "password", 128),
        role=required_str(data, "role", 10),
    )
    return user.to_dict(), 201


@bp.post("/login")
def login():
    data = get_json()
    user = services.authenticate(
        email=required_str(data, "email", 160),
        password=required_str(data, "password", 128),
    )
    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return {"access_token": token, "user": user.to_dict()}


@bp.get("/me")
@jwt_required()
def me():
    data = current_user.to_dict()
    if current_user.personal:
        data["personal_name"] = current_user.personal.name
    return data


@bp.post("/link")
@role_required("aluno")
def link():
    data = get_json()
    personal = services.link_student(current_user, required_str(data, "invite_code", 8))
    return {"personal_id": personal.id, "personal_name": personal.name}


@bp.get("/students")
@role_required("personal")
def students():
    return {"students": services.list_students(current_user)}
