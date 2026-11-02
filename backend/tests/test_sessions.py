def _item_id(workout):
    return workout["exercises"][0]["id"]


# RF06
def test_aluno_registra_sessao_com_series(client, student, workout):
    response = client.post(
        "/api/sessions",
        json={
            "workout_id": workout["id"],
            "sets": [
                {"workout_exercise_id": _item_id(workout), "set_number": 1,
                 "reps_done": 12, "load_kg": 40},
                {"workout_exercise_id": _item_id(workout), "set_number": 2,
                 "reps_done": 10, "load_kg": 42.5},
            ],
        },
        headers=student["headers"],
    )
    assert response.status_code == 201
    assert [s["load_kg"] for s in response.json["sets"]] == [40, 42.5]


def test_registrar_mesma_serie_corrige_o_valor(client, student, workout):
    session = client.post(
        "/api/sessions", json={"workout_id": workout["id"]}, headers=student["headers"]
    ).json
    url = f"/api/sessions/{session['id']}/sets"
    serie = {"workout_exercise_id": _item_id(workout), "set_number": 1, "reps_done": 10}

    client.put(url, json={**serie, "load_kg": 40}, headers=student["headers"])
    client.put(url, json={**serie, "load_kg": 45}, headers=student["headers"])

    detalhe = client.get(f"/api/sessions/{session['id']}", headers=student["headers"]).json
    assert len(detalhe["sets"]) == 1
    assert detalhe["sets"][0]["load_kg"] == 45


def test_carga_negativa_e_rejeitada(client, student, workout):
    session = client.post(
        "/api/sessions", json={"workout_id": workout["id"]}, headers=student["headers"]
    ).json
    response = client.put(
        f"/api/sessions/{session['id']}/sets",
        json={"workout_exercise_id": _item_id(workout), "set_number": 1,
              "reps_done": 10, "load_kg": -5},
        headers=student["headers"],
    )
    assert response.status_code == 400


def test_numero_da_serie_nao_passa_do_prescrito(client, student, workout):
    session = client.post(
        "/api/sessions", json={"workout_id": workout["id"]}, headers=student["headers"]
    ).json
    response = client.put(
        f"/api/sessions/{session['id']}/sets",
        json={"workout_exercise_id": _item_id(workout), "set_number": 4,
              "reps_done": 10, "load_kg": 40},
        headers=student["headers"],
    )
    assert response.status_code == 400


def test_nao_registra_sessao_em_ficha_inativa(client, personal, student, workout):
    client.put(
        f"/api/workouts/{workout['id']}", json={"is_active": False}, headers=personal["headers"]
    )
    response = client.post(
        "/api/sessions", json={"workout_id": workout["id"]}, headers=student["headers"]
    )
    assert response.status_code == 404


def test_personal_nao_registra_sessao(client, personal, workout):
    response = client.post(
        "/api/sessions", json={"workout_id": workout["id"]}, headers=personal["headers"]
    )
    assert response.status_code == 403


# RF07
def test_historico_ordenado_da_sessao_mais_recente(client, personal, student, workout):
    for data in ["2026-10-01T08:00:00", "2026-10-15T08:00:00", "2026-10-08T08:00:00"]:
        client.post(
            "/api/sessions",
            json={"workout_id": workout["id"], "performed_at": data},
            headers=student["headers"],
        )

    datas_aluno = [
        s["performed_at"]
        for s in client.get("/api/sessions", headers=student["headers"]).json["sessions"]
    ]
    assert datas_aluno == ["2026-10-15T08:00:00", "2026-10-08T08:00:00", "2026-10-01T08:00:00"]

    response = client.get(
        f"/api/sessions?student_id={student['user']['id']}", headers=personal["headers"]
    )
    assert len(response.json["sessions"]) == 3


def test_aluno_nao_ve_sessao_de_outro_aluno(client, student, workout, make_aluno):
    session = client.post(
        "/api/sessions", json={"workout_id": workout["id"]}, headers=student["headers"]
    ).json
    outro = make_aluno("curioso@teste.com")
    response = client.get(f"/api/sessions/{session['id']}", headers=outro["headers"])
    assert response.status_code == 404


def test_personal_nao_ve_historico_de_aluno_alheio(client, student, other_personal):
    response = client.get(
        f"/api/sessions?student_id={student['user']['id']}", headers=other_personal["headers"]
    )
    assert response.status_code == 404


# RF08
def test_evolucao_da_carga_maxima_por_exercicio(client, personal, student, workout, exercise):
    for data, cargas in [("2026-10-01T08:00:00", [40, 42]), ("2026-10-08T08:00:00", [45, 44])]:
        client.post(
            "/api/sessions",
            json={
                "workout_id": workout["id"],
                "performed_at": data,
                "sets": [
                    {"workout_exercise_id": _item_id(workout), "set_number": n,
                     "reps_done": 10, "load_kg": carga}
                    for n, carga in enumerate(cargas, start=1)
                ],
            },
            headers=student["headers"],
        )

    response = client.get(
        f"/api/sessions/progress?exercise_id={exercise['id']}", headers=student["headers"]
    )
    assert [p["max_load_kg"] for p in response.json["points"]] == [42, 45]

    response = client.get(
        f"/api/sessions/progress?exercise_id={exercise['id']}&student_id={student['user']['id']}",
        headers=personal["headers"],
    )
    assert len(response.json["points"]) == 2

    response = client.get("/api/sessions/progress/exercises", headers=student["headers"])
    assert [e["name"] for e in response.json["exercises"]] == ["Supino reto"]
