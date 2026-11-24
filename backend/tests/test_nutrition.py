from datetime import date, timedelta

import pytest

MEALS = [
    {"name": "Cafe da manha", "time": "07:30", "foods": "2 ovos, 1 pao integral", "kcal": 350},
    {"name": "Almoco", "time": "12:30", "foods": "Arroz, feijao, frango e salada", "kcal": 650},
    {"name": "Jantar", "foods": "Omelete com legumes", "kcal": 400},
]


@pytest.fixture
def patient(client, nutri, student):
    """O mesmo aluno do personal, agora vinculado tambem a nutricionista."""
    response = client.post(
        "/api/auth/link",
        json={"invite_code": nutri["user"]["invite_code"]},
        headers=student["headers"],
    )
    assert response.status_code == 200
    assert response.json["role"] == "nutricionista"
    return student


@pytest.fixture
def plan(client, nutri, patient):
    response = client.post(
        "/api/nutrition/plans",
        json={
            "student_id": patient["user"]["id"],
            "name": "Plano de ganho de massa",
            "goal": "Ganhar 3 kg em 3 meses",
            "meals": MEALS,
        },
        headers=nutri["headers"],
    )
    assert response.status_code == 201, response.json
    return response.json


# RF10
def test_nutricionista_recebe_codigo_de_convite(nutri):
    assert len(nutri["user"]["invite_code"]) == 8


def test_aluno_fica_com_personal_e_nutricionista(client, personal, patient):
    me = client.get("/api/auth/me", headers=patient["headers"]).json
    assert me["personal_name"] == "Paula Personal"
    assert me["nutritionist_name"] == "Nina Nutri"


# RF11
def test_nutricionista_monta_plano_alimentar(plan):
    assert plan["is_active"] is True
    assert [m["position"] for m in plan["meals"]] == [1, 2, 3]
    assert plan["total_kcal"] == 1400


def test_novo_plano_desativa_o_anterior(client, nutri, patient, plan):
    novo = client.post(
        "/api/nutrition/plans",
        json={"student_id": patient["user"]["id"], "name": "Plano 2", "meals": MEALS[:1]},
        headers=nutri["headers"],
    ).json
    planos = client.get("/api/nutrition/plans", headers=patient["headers"]).json["plans"]
    assert [p["id"] for p in planos] == [novo["id"]]


def test_horario_invalido_retorna_400(client, nutri, patient):
    response = client.post(
        "/api/nutrition/plans",
        json={
            "student_id": patient["user"]["id"],
            "name": "Plano",
            "meals": [{"name": "Lanche", "time": "25:00", "foods": "Fruta"}],
        },
        headers=nutri["headers"],
    )
    assert response.status_code == 400


def test_nao_monta_plano_para_quem_nao_e_paciente(client, nutri, student):
    response = client.post(
        "/api/nutrition/plans",
        json={"student_id": student["user"]["id"], "name": "Plano", "meals": MEALS},
        headers=nutri["headers"],
    )
    assert response.status_code == 404


def test_personal_nao_acessa_rotas_do_nutricionista(client, personal):
    assert client.get("/api/nutrition/patients", headers=personal["headers"]).status_code == 403


# RF12
def test_aluno_marca_e_desmarca_refeicao_do_dia(client, patient, plan):
    meal_id = plan["meals"][0]["id"]
    hoje = client.put(
        f"/api/nutrition/meals/{meal_id}/check", json={"done": True}, headers=patient["headers"]
    ).json
    assert hoje["done"] == 1
    assert hoje["total"] == 3
    assert hoje["kcal_done"] == 350

    hoje = client.put(
        f"/api/nutrition/meals/{meal_id}/check", json={"done": False}, headers=patient["headers"]
    ).json
    assert hoje["done"] == 0


def test_marcar_duas_vezes_nao_duplica(client, patient, plan):
    meal_id = plan["meals"][1]["id"]
    for _ in range(2):
        client.put(
            f"/api/nutrition/meals/{meal_id}/check", json={"done": True}, headers=patient["headers"]
        )
    assert client.get("/api/nutrition/today", headers=patient["headers"]).json["done"] == 1


def test_nao_marca_dia_futuro(client, patient, plan):
    amanha = (date.today() + timedelta(days=1)).isoformat()
    response = client.put(
        f"/api/nutrition/meals/{plan['meals'][0]['id']}/check",
        json={"done": True, "day": amanha},
        headers=patient["headers"],
    )
    assert response.status_code == 400


def test_plano_com_refeicoes_marcadas_nao_e_excluido(client, nutri, patient, plan):
    client.put(
        f"/api/nutrition/meals/{plan['meals'][0]['id']}/check",
        json={"done": True},
        headers=patient["headers"],
    )
    response = client.delete(f"/api/nutrition/plans/{plan['id']}", headers=nutri["headers"])
    assert response.status_code == 409


def test_adesao_dos_ultimos_dias(client, nutri, patient, plan):
    for meal in plan["meals"][:2]:
        client.put(
            f"/api/nutrition/meals/{meal['id']}/check",
            json={"done": True},
            headers=patient["headers"],
        )
    dias = client.get(
        f"/api/nutrition/adherence?student_id={patient['user']['id']}&days=7",
        headers=nutri["headers"],
    ).json["days"]
    assert len(dias) == 7
    assert dias[-1] == {"day": date.today().isoformat(), "done": 2, "total": 3, "percent": 67}


# RF13
def test_aluno_registra_peso_e_nutricionista_ve(client, nutri, patient):
    ontem = (date.today() - timedelta(days=1)).isoformat()
    client.post(
        "/api/nutrition/weights", json={"weight_kg": 70.5, "day": ontem}, headers=patient["headers"]
    )
    client.post("/api/nutrition/weights", json={"weight_kg": 70.1}, headers=patient["headers"])
    client.post(
        "/api/nutrition/weights", json={"weight_kg": 70.2}, headers=patient["headers"]
    )  # corrige hoje

    pesos = client.get(
        f"/api/nutrition/weights?student_id={patient['user']['id']}", headers=nutri["headers"]
    ).json["weights"]
    assert [p["weight_kg"] for p in pesos] == [70.5, 70.2]


def test_peso_fora_do_limite_retorna_400(client, patient):
    response = client.post(
        "/api/nutrition/weights", json={"weight_kg": 5}, headers=patient["headers"]
    )
    assert response.status_code == 400


# RF14
def test_lista_de_pacientes_com_resumo(client, nutri, patient, plan):
    client.post("/api/nutrition/weights", json={"weight_kg": 70}, headers=patient["headers"])
    pacientes = client.get("/api/nutrition/patients", headers=nutri["headers"]).json["patients"]
    assert pacientes[0]["name"] == "Ana Aluna"
    assert pacientes[0]["plan_name"] == "Plano de ganho de massa"
    assert pacientes[0]["last_weight"]["weight_kg"] == 70
