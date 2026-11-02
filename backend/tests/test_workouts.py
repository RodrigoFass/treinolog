# RF04
def test_personal_monta_ficha_para_aluno(workout):
    assert workout["name"] == "Treino A"
    assert workout["is_active"] is True
    item = workout["exercises"][0]
    assert item["position"] == 1
    assert item["sets"] == 3
    assert item["reps"] == "10-12"
    assert item["suggested_load_kg"] == 40


def test_nao_monta_ficha_para_aluno_de_outro_personal(client, other_personal, student):
    response = client.post(
        "/api/workouts",
        json={"student_id": student["user"]["id"], "name": "Treino A"},
        headers=other_personal["headers"],
    )
    assert response.status_code == 404


def test_series_devem_ficar_entre_1_e_20(client, personal, student, exercise):
    response = client.post(
        "/api/workouts",
        json={
            "student_id": student["user"]["id"],
            "name": "Treino B",
            "exercises": [{"exercise_id": exercise["id"], "sets": 21, "reps": "10"}],
        },
        headers=personal["headers"],
    )
    assert response.status_code == 400


def test_nao_usa_exercicio_de_outro_catalogo(client, other_personal, personal, student):
    alheio = client.post(
        "/api/exercises",
        json={"name": "Remada", "muscle_group": "Costas"},
        headers=other_personal["headers"],
    ).json
    response = client.post(
        "/api/workouts",
        json={
            "student_id": student["user"]["id"],
            "name": "Treino B",
            "exercises": [{"exercise_id": alheio["id"], "sets": 3, "reps": "10"}],
        },
        headers=personal["headers"],
    )
    assert response.status_code == 400


def test_adiciona_e_edita_exercicio_da_ficha(client, personal, exercise, workout):
    url = f"/api/workouts/{workout['id']}/exercises"
    novo = client.post(
        url, json={"exercise_id": exercise["id"], "sets": 4, "reps": "8"},
        headers=personal["headers"],
    )
    assert novo.status_code == 201
    assert novo.json["position"] == 2

    editado = client.put(
        f"{url}/{novo.json['id']}", json={"suggested_load_kg": 50}, headers=personal["headers"]
    )
    assert editado.json["suggested_load_kg"] == 50
    assert editado.json["sets"] == 4


# RF05
def test_aluno_ve_apenas_fichas_ativas(client, personal, student, workout):
    client.put(
        f"/api/workouts/{workout['id']}", json={"is_active": False}, headers=personal["headers"]
    )
    response = client.get("/api/workouts", headers=student["headers"])
    assert response.json["workouts"] == []

    response = client.get("/api/workouts", headers=personal["headers"])
    assert len(response.json["workouts"]) == 1


def test_aluno_nao_ve_ficha_de_outro_aluno(client, make_aluno, workout):
    outro = make_aluno("outro.aluno@teste.com")
    response = client.get(f"/api/workouts/{workout['id']}", headers=outro["headers"])
    assert response.status_code == 404


def test_aluno_nao_altera_ficha(client, student, workout):
    response = client.put(
        f"/api/workouts/{workout['id']}", json={"name": "Hack"}, headers=student["headers"]
    )
    assert response.status_code == 403


def test_nao_exclui_ficha_com_treinos_registrados(client, personal, student, workout):
    client.post("/api/sessions", json={"workout_id": workout["id"]}, headers=student["headers"])
    response = client.delete(f"/api/workouts/{workout['id']}", headers=personal["headers"])
    assert response.status_code == 409


def test_exclui_ficha_sem_treinos(client, personal, workout):
    response = client.delete(f"/api/workouts/{workout['id']}", headers=personal["headers"])
    assert response.status_code == 204
