from flask import Blueprint
from flask_jwt_extended import current_user, jwt_required

from treinolog.achievements import services
from treinolog.utils import query_int

bp = Blueprint("achievements", __name__)


@bp.get("")
@jwt_required()
def summary():
    weeks = query_int("weeks") or 12
    return services.summary(current_user, query_int("student_id"), min(weeks, 52))
