from flask import Blueprint
from flask_jwt_extended import create_access_token, current_user, jwt_required

from treinolog.auth import services
from treinolog.ext.jwt import role_required
from treinolog.auth.schemas import LinkSchema, LoginSchema, RegisterSchema
from treinolog.utils import validate_json

bp = Blueprint("auth", __name__)


@bp.post("/register")
def register():
    data = validate_json(RegisterSchema)
    user = services.register_user(**data)
    return user.to_dict(), 201


@bp.post("/login")
def login():
    data = validate_json(LoginSchema)
    user = services.authenticate(**data)
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
    data = validate_json(LinkSchema)
    personal = services.link_student(current_user, data["invite_code"])
    return {"personal_id": personal.id, "personal_name": personal.name}


@bp.get("/students")
@role_required("personal")
def students():
    return {"students": services.list_students(current_user)}
