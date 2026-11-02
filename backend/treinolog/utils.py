from datetime import datetime

from flask import request
from werkzeug.exceptions import BadRequest


def get_json() -> dict:
    """Le o corpo JSON da requisicao ou responde 400."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise BadRequest("Corpo da requisicao deve ser um objeto JSON")
    return data


def required_str(data: dict, field: str, max_len: int) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise BadRequest(f"Campo '{field}' e obrigatorio")
    value = value.strip()
    if len(value) > max_len:
        raise BadRequest(f"Campo '{field}' deve ter no maximo {max_len} caracteres")
    return value


def optional_str(data: dict, field: str, max_len: int | None = None) -> str | None:
    value = data.get(field)
    if value is None:
        return None
    if not isinstance(value, str):
        raise BadRequest(f"Campo '{field}' deve ser texto")
    value = value.strip()
    if max_len and len(value) > max_len:
        raise BadRequest(f"Campo '{field}' deve ter no maximo {max_len} caracteres")
    return value or None


def to_int(data: dict, field: str, min_value: int, max_value: int, required: bool = True):
    value = data.get(field)
    if value is None:
        if required:
            raise BadRequest(f"Campo '{field}' e obrigatorio")
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise BadRequest(f"Campo '{field}' deve ser um numero inteiro")
    if not min_value <= value <= max_value:
        raise BadRequest(f"Campo '{field}' deve estar entre {min_value} e {max_value}")
    return value


def to_float(data: dict, field: str, min_value: float, max_value: float, required: bool = True):
    value = data.get(field)
    if value is None:
        if required:
            raise BadRequest(f"Campo '{field}' e obrigatorio")
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise BadRequest(f"Campo '{field}' deve ser numerico")
    if not min_value <= value <= max_value:
        raise BadRequest(f"Campo '{field}' deve estar entre {min_value} e {max_value}")
    return round(float(value), 2)


def to_datetime(data: dict, field: str) -> datetime | None:
    value = data.get(field)
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        raise BadRequest(f"Campo '{field}' deve estar no formato ISO (AAAA-MM-DDTHH:MM)")


def query_int(name: str) -> int | None:
    value = request.args.get(name)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        raise BadRequest(f"Parametro '{name}' deve ser inteiro")
