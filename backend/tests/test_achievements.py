from datetime import date, datetime, timedelta

from treinolog.achievements.services import _streaks


def _treinar(client, student, workout, dia: date, com_serie: bool = True):
    sets = []
    if com_serie:
        sets = [
            {
                "workout_exercise_id": workout["exercises"][0]["id"],
                "set_number": 1,
                "reps_done": 10,
                "load_kg": 40,
            }
        ]
    response = client.post(
        "/api/sessions",
        json={
            "workout_id": workout["id"],
            "performed_at": datetime.combine(dia, datetime.min.time()).replace(hour=18).isoformat(),
            "sets": sets,
        },
        headers=student["headers"],
    )
    assert response.status_code == 201, response.json


# Regra da ofensiva (sem banco)
def test_ofensiva_conta_dias_seguidos_ate_hoje():
    hoje = date(2026, 11, 23)
    dias = {hoje, hoje - timedelta(days=1), hoje - timedelta(days=2), hoje - timedelta(days=5)}
    assert _streaks(dias, hoje) == (3, 3)


def test_hoje_sem_atividade_ainda_nao_quebra_a_ofensiva():
    hoje = date(2026, 11, 23)
    dias = {hoje - timedelta(days=1), hoje - timedelta(days=2)}
    assert _streaks(dias, hoje) == (2, 2)


def test_um_dia_sem_atividade_zera_a_ofensiva_mas_guarda_o_recorde():
    hoje = date(2026, 11, 23)
    dias = {hoje - timedelta(days=d) for d in (2, 3, 4, 5)}
    assert _streaks(dias, hoje) == (0, 4)


# RF15
def test_treinos_aparecem_no_calendario_e_somam_na_ofensiva(client, student, workout):
    hoje = date.today()
    for dias_atras in (0, 1, 2):
        _treinar(client, student, workout, hoje - timedelta(days=dias_atras))

    resumo = client.get("/api/achievements", headers=student["headers"]).json
    assert resumo["current_streak"] == 3
    assert resumo["best_streak"] == 3
    assert resumo["active_today"] is True
    marcados = {d["day"] for d in resumo["calendar"] if d["trained"]}
    assert hoje.isoformat() in marcados
    assert len(resumo["calendar"]) == 12 * 7

    conquistas = {b["id"]: b["unlocked"] for b in resumo["badges"]}
    assert conquistas["primeiro-treino"] is True
    assert conquistas["ofensiva-3"] is True
    assert conquistas["ofensiva-7"] is False


def test_sessao_sem_serie_nao_conta(client, student, workout):
    _treinar(client, student, workout, date.today(), com_serie=False)
    resumo = client.get("/api/achievements", headers=student["headers"]).json
    assert resumo["current_streak"] == 0


def test_dia_com_todas_as_refeicoes_conta_na_ofensiva(client, nutri, student):
    client.post(
        "/api/auth/link",
        json={"invite_code": nutri["user"]["invite_code"]},
        headers=student["headers"],
    )
    plano = client.post(
        "/api/nutrition/plans",
        json={
            "student_id": student["user"]["id"],
            "name": "Plano",
            "meals": [
                {"name": "Almoco", "foods": "Arroz e feijao"},
                {"name": "Jantar", "foods": "Sopa"},
            ],
        },
        headers=nutri["headers"],
    ).json
    refeicoes = [m["id"] for m in plano["meals"]]

    client.put(
        f"/api/nutrition/meals/{refeicoes[0]}/check",
        json={"done": True},
        headers=student["headers"],
    )
    assert client.get("/api/achievements", headers=student["headers"]).json["current_streak"] == 0

    client.put(
        f"/api/nutrition/meals/{refeicoes[1]}/check",
        json={"done": True},
        headers=student["headers"],
    )
    resumo = client.get(
        f"/api/achievements?student_id={student['user']['id']}", headers=nutri["headers"]
    ).json
    assert resumo["current_streak"] == 1
    assert any(d["diet"] for d in resumo["calendar"])


def test_personal_ve_a_ofensiva_do_aluno_mas_nao_de_aluno_alheio(
    client, personal, other_personal, student
):
    url = f"/api/achievements?student_id={student['user']['id']}"
    assert client.get(url, headers=personal["headers"]).status_code == 200
    assert client.get(url, headers=other_personal["headers"]).status_code == 404


# Medalhas de tempo sem falha
def test_semanas_seguidas_batendo_a_meta_de_treinos():
    from treinolog.achievements.services import WEEKLY_GOAL, _training_weeks

    hoje = date(2026, 11, 25)  # quarta-feira
    domingo = date(2026, 11, 22)
    dias = set()
    for semana in (1, 2, 3):  # tres semanas completas antes desta
        inicio = domingo - timedelta(days=7 * semana)
        dias |= {inicio + timedelta(days=d) for d in range(WEEKLY_GOAL)}
    assert _training_weeks(dias, hoje) == (3, 3)

    # uma semana sem bater a meta quebra a sequencia, mas o recorde fica
    sem_falha_recente = {d for d in dias if d >= domingo - timedelta(days=7)}
    antigas = {d - timedelta(days=21) for d in dias}
    assert _training_weeks(sem_falha_recente | antigas, hoje) == (1, 3)


def test_medalha_de_dieta_sem_falha(client, nutri, student):
    from treinolog.ext.db import db
    from treinolog.nutrition.models import MealLog

    client.post(
        "/api/auth/link",
        json={"invite_code": nutri["user"]["invite_code"]},
        headers=student["headers"],
    )
    plano = client.post(
        "/api/nutrition/plans",
        json={
            "student_id": student["user"]["id"],
            "name": "Plano",
            "meals": [{"name": "Almoco", "foods": "Arroz e feijao"}],
        },
        headers=nutri["headers"],
    ).json
    for dias_atras in range(1, 8):
        db.session.add(
            MealLog(
                student_id=student["user"]["id"],
                meal_id=plano["meals"][0]["id"],
                day=date.today() - timedelta(days=dias_atras),
            )
        )
    db.session.commit()

    resumo = client.get("/api/achievements", headers=student["headers"]).json
    assert resumo["diet_streak"] == {"current": 7, "best": 7}
    medalhas = {m["id"]: m for m in resumo["medals"]}
    assert medalhas["dieta-bronze"]["unlocked"] is True
    assert medalhas["dieta-prata"]["unlocked"] is False
    assert medalhas["dieta-prata"]["progress"] == 7
    assert medalhas["treino-bronze"]["unlocked"] is False
