from treinolog import create_app
from treinolog.ext.db import db

# Testes da validacao com Pydantic e do tratamento de erros


def test_mensagem_de_campo_obrigatorio(client):
    response = client.post("/api/auth/register", json={"name": "Joao"})
    assert response.status_code == 400
    assert "email" in response.json["erro"]


def test_email_invalido_no_cadastro(client):
    response = client.post(
        "/api/auth/register",
        json={"name": "Joao", "email": "joao", "password": "senha123", "role": "aluno"},
    )
    assert response.status_code == 400
    assert "email" in response.json["erro"]


def test_senha_curta_no_cadastro(client):
    response = client.post(
        "/api/auth/register",
        json={"name": "Joao", "email": "joao@teste.com", "password": "123", "role": "aluno"},
    )
    assert response.status_code == 400
    assert "password" in response.json["erro"]


def test_nome_so_com_espacos_e_rejeitado(client, personal):
    response = client.post(
        "/api/exercises",
        json={"name": "   ", "muscle_group": "Peito"},
        headers=personal["headers"],
    )
    assert response.status_code == 400


def test_carga_negativa_na_ficha(client, personal, student, exercise):
    response = client.post(
        "/api/workouts",
        json={
            "student_id": student["user"]["id"],
            "name": "Treino C",
            "exercises": [
                {"exercise_id": exercise["id"], "sets": 3, "reps": "10", "suggested_load_kg": -1}
            ],
        },
        headers=personal["headers"],
    )
    assert response.status_code == 400
    assert "suggested_load_kg" in response.json["erro"]


def test_data_invalida_na_sessao(client, student, workout):
    response = client.post(
        "/api/sessions",
        json={"workout_id": workout["id"], "performed_at": "ontem"},
        headers=student["headers"],
    )
    assert response.status_code == 400


def test_corpo_que_nao_e_json(client):
    response = client.post("/api/auth/login", data="nao sou json")
    assert response.status_code == 400


def test_rota_inexistente_responde_json(client):
    response = client.get("/api/nao-existe")
    assert response.status_code == 404
    assert "erro" in response.json


def test_erro_inesperado_responde_500_em_json():
    app = create_app("testing")

    @app.get("/api/quebra")
    def quebra():
        raise RuntimeError("falha simulada")

    with app.app_context():
        db.create_all()
        response = app.test_client().get("/api/quebra")

    assert response.status_code == 500
    assert response.json == {"erro": "Erro interno no servidor"}
