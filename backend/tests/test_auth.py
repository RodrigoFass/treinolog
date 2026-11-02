from treinolog.auth.models import User
from treinolog.ext.db import db


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200


def test_rota_inexistente_responde_404_em_json(client):
    response = client.get("/api/rota-inexistente")
    assert response.status_code == 404
    assert "erro" in response.json


# RF01
def test_cadastro_de_personal_gera_codigo_de_convite(personal):
    assert personal["user"]["role"] == "personal"
    assert len(personal["user"]["invite_code"]) == 8


def test_senha_e_guardada_apenas_como_hash(app, personal):
    user = db.session.scalar(db.select(User).filter_by(email="paula@teste.com"))
    assert user.password_hash != "senha123"
    assert user.check_password("senha123")


def test_nao_aceita_email_duplicado(client, personal):
    response = client.post(
        "/api/auth/register",
        json={"name": "X", "email": "PAULA@teste.com", "password": "senha123", "role": "aluno"},
    )
    assert response.status_code == 409


def test_nao_aceita_perfil_invalido(client):
    response = client.post(
        "/api/auth/register",
        json={"name": "X", "email": "x@teste.com", "password": "senha123", "role": "admin"},
    )
    assert response.status_code == 400


def test_login_com_senha_errada_retorna_401(client, personal):
    response = client.post(
        "/api/auth/login", json={"email": "paula@teste.com", "password": "errada"}
    )
    assert response.status_code == 401


def test_rota_protegida_sem_token_retorna_401(client):
    assert client.get("/api/auth/me").status_code == 401


# RF02
def test_aluno_se_vincula_ao_personal_por_codigo(client, personal, student):
    response = client.get("/api/auth/me", headers=student["headers"])
    assert response.json["personal_id"] == personal["user"]["id"]
    assert response.json["personal_name"] == "Paula Personal"


def test_codigo_de_convite_inexistente_retorna_404(client, make_aluno):
    aluno = make_aluno("solto@teste.com")
    response = client.post(
        "/api/auth/link", json={"invite_code": "ZZZZZZZZ"}, headers=aluno["headers"]
    )
    assert response.status_code == 404


def test_personal_nao_pode_usar_rota_de_vinculo(client, personal):
    response = client.post(
        "/api/auth/link", json={"invite_code": "ABCDEFGH"}, headers=personal["headers"]
    )
    assert response.status_code == 403


# RF09
def test_painel_lista_alunos_com_data_do_ultimo_treino(client, personal, student, workout):
    response = client.get("/api/auth/students", headers=personal["headers"])
    assert response.json["students"][0]["last_workout_at"] is None

    client.post(
        "/api/sessions",
        json={"workout_id": workout["id"], "performed_at": "2026-10-20T08:00:00"},
        headers=student["headers"],
    )
    response = client.get("/api/auth/students", headers=personal["headers"])
    assert response.json["students"][0]["last_workout_at"] == "2026-10-20T08:00:00"


def test_painel_nao_mostra_alunos_de_outro_personal(client, student, other_personal):
    response = client.get("/api/auth/students", headers=other_personal["headers"])
    assert response.json["students"] == []
