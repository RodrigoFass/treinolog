# RF03
def test_personal_cadastra_e_lista_exercicios(client, personal, exercise):
    response = client.get("/api/exercises", headers=personal["headers"])
    assert response.status_code == 200
    assert [e["name"] for e in response.json["exercises"]] == ["Supino reto"]


def test_filtra_exercicios_por_grupo_muscular(client, personal, exercise):
    client.post(
        "/api/exercises",
        json={"name": "Agachamento", "muscle_group": "Pernas"},
        headers=personal["headers"],
    )
    response = client.get("/api/exercises?muscle_group=Pernas", headers=personal["headers"])
    assert [e["name"] for e in response.json["exercises"]] == ["Agachamento"]


def test_nome_de_exercicio_e_unico_por_personal(client, personal, other_personal, exercise):
    duplicado = {"name": "Supino reto", "muscle_group": "Peito"}
    assert client.post(
        "/api/exercises", json=duplicado, headers=personal["headers"]
    ).status_code == 409
    assert client.post(
        "/api/exercises", json=duplicado, headers=other_personal["headers"]
    ).status_code == 201


def test_edita_exercicio(client, personal, exercise):
    response = client.put(
        f"/api/exercises/{exercise['id']}",
        json={"description": "Pegada media"},
        headers=personal["headers"],
    )
    assert response.status_code == 200
    assert response.json["description"] == "Pegada media"


def test_exclui_exercicio_sem_uso(client, personal, exercise):
    response = client.delete(f"/api/exercises/{exercise['id']}", headers=personal["headers"])
    assert response.status_code == 204


def test_nao_exclui_exercicio_em_uso_numa_ficha(client, personal, exercise, workout):
    response = client.delete(f"/api/exercises/{exercise['id']}", headers=personal["headers"])
    assert response.status_code == 409


def test_personal_nao_acessa_exercicio_de_outro(client, other_personal, exercise):
    response = client.get(f"/api/exercises/{exercise['id']}", headers=other_personal["headers"])
    assert response.status_code == 404


def test_aluno_nao_acessa_catalogo(client, student):
    assert client.get("/api/exercises", headers=student["headers"]).status_code == 403


def test_campos_obrigatorios_do_exercicio(client, personal):
    response = client.post("/api/exercises", json={"name": "X"}, headers=personal["headers"])
    assert response.status_code == 400
