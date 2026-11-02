import pytest

from treinolog import create_app
from treinolog.ext.db import db


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def _register_and_login(client, name, email, role):
    response = client.post(
        "/api/auth/register",
        json={"name": name, "email": email, "password": "senha123", "role": role},
    )
    assert response.status_code == 201, response.json
    login = client.post("/api/auth/login", json={"email": email, "password": "senha123"})
    return {
        "user": login.json["user"],
        "headers": {"Authorization": f"Bearer {login.json['access_token']}"},
    }


@pytest.fixture
def personal(client):
    return _register_and_login(client, "Paula Personal", "paula@teste.com", "personal")


@pytest.fixture
def other_personal(client):
    return _register_and_login(client, "Outro Personal", "outro@teste.com", "personal")


@pytest.fixture
def student(client, personal):
    """Aluno ja vinculado ao personal pelo codigo de convite."""
    aluno = _register_and_login(client, "Ana Aluna", "ana@teste.com", "aluno")
    response = client.post(
        "/api/auth/link",
        json={"invite_code": personal["user"]["invite_code"]},
        headers=aluno["headers"],
    )
    assert response.status_code == 200
    return aluno


@pytest.fixture
def make_aluno(client):
    def factory(email):
        return _register_and_login(client, "Aluno Extra", email, "aluno")

    return factory


@pytest.fixture
def exercise(client, personal):
    response = client.post(
        "/api/exercises",
        json={"name": "Supino reto", "muscle_group": "Peito"},
        headers=personal["headers"],
    )
    return response.json


@pytest.fixture
def workout(client, personal, student, exercise):
    response = client.post(
        "/api/workouts",
        json={
            "student_id": student["user"]["id"],
            "name": "Treino A",
            "exercises": [
                {
                    "exercise_id": exercise["id"],
                    "sets": 3,
                    "reps": "10-12",
                    "suggested_load_kg": 40,
                    "rest_seconds": 90,
                }
            ],
        },
        headers=personal["headers"],
    )
    assert response.status_code == 201, response.json
    return response.json
