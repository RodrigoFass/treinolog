# TreinoLog

Aplicação web em que o personal trainer monta as fichas de treino dos alunos e o aluno registra, durante o treino, a carga e as repetições de cada série.

**Integrantes:** Rodrigo Fassarella Leite e Pedro Henrique Meneghelli

## Arquitetura

Cliente-servidor em três camadas, a mesma do TaskFlow:

| Camada | Tecnologias |
|---|---|
| Frontend (`frontend/`) | Vue 3, Vite, Vue Router, Pinia, Axios, Chart.js |
| Backend (`backend/`) | Python 3.12, Flask (Application Factory + blueprints), Flask-SQLAlchemy, Flask-Migrate, Flask-JWT-Extended |
| Banco | SQLite em desenvolvimento e testes; MySQL em produção |

```
backend/
├── app.py                  # ponto de entrada (create_app)
├── tasks.py                # automação com invoke
├── pyproject.toml
├── migrations/             # Flask-Migrate (Alembic)
├── treinolog/
│   ├── __init__.py         # create_app()
│   ├── config.py           # Development / Testing / Production
│   ├── utils.py            # validação dos dados de entrada
│   ├── ext/                # db, jwt, errors, cli
│   ├── auth/               # users: cadastro, login, vínculo, painel
│   ├── exercises/          # exercises: catálogo do personal
│   ├── workouts/           # workouts + workout_exercises: fichas
│   └── sessions/           # workout_sessions + set_logs: treinos e evolução
└── tests/                  # PyTest + pytest-flask
```

Cada módulo de domínio tem `models.py` (tabelas), `services.py` (regras de negócio) e `routes.py` (blueprint da API).

## Como rodar

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -e ".[dev,test]"
copy .env.example .env.dev      # ajuste SECRET_KEY e JWT_SECRET_KEY
flask --app app db upgrade      # cria as tabelas
flask --app app seed            # opcional: personal e aluno de demonstração
invoke run                      # API em http://127.0.0.1:5000
```

Contas criadas pelo `seed`: `personal@treinolog.dev` e `aluno@treinolog.dev`, ambas com a senha `demo1234`.

### Frontend

```powershell
cd frontend
npm install
npm run dev                     # http://localhost:5173 (repassa /api para a porta 5000)
```

### Testes

```powershell
cd backend
invoke test        # ou: pytest -v
invoke cov         # cobertura
```

### Produção (MySQL)

```powershell
pip install -e ".[mysql]"
$env:FLASK_CONFIG = "production"
$env:DATABASE_URL = "mysql+pymysql://usuario:senha@host/treinolog?charset=utf8mb4"
flask --app app db upgrade
```

## API

Todas as rotas, exceto cadastro, login e health, exigem o cabeçalho `Authorization: Bearer <token>`. Erros voltam como `{"erro": "mensagem"}`.

| Método | Rota | Perfil | Requisito |
|---|---|---|---|
| POST | `/api/auth/register` | — | RF01 |
| POST | `/api/auth/login` | — | RF01 |
| GET | `/api/auth/me` | todos | RF01 |
| POST | `/api/auth/link` | aluno | RF02 |
| GET | `/api/auth/students` | personal | RF09 |
| GET/POST | `/api/exercises` | personal | RF03 |
| GET/PUT/DELETE | `/api/exercises/<id>` | personal | RF03 |
| GET | `/api/workouts` | todos (aluno vê só as ativas) | RF05 |
| POST | `/api/workouts` | personal | RF04 |
| GET/PUT/DELETE | `/api/workouts/<id>` | personal (GET: aluno dono também) | RF04 |
| POST | `/api/workouts/<id>/exercises` | personal | RF04 |
| PUT/DELETE | `/api/workouts/<id>/exercises/<item_id>` | personal | RF04 |
| GET | `/api/sessions` | todos | RF07 |
| POST | `/api/sessions` | aluno | RF06 |
| GET | `/api/sessions/<id>` | todos | RF07 |
| PUT/DELETE | `/api/sessions/<id>` | aluno | RF06 |
| PUT | `/api/sessions/<id>/sets` | aluno | RF06 |
| GET | `/api/sessions/progress/exercises` | todos | RF08 |
| GET | `/api/sessions/progress?exercise_id=` | todos | RF08 |

O personal consulta histórico e evolução de um aluno passando `?student_id=`.

## Regras de negócio implementadas

- Senha guardada só como hash (`werkzeug.security`).
- Cada rota verifica o perfil e o dono do recurso. O aluno só acessa os próprios dados, e o personal só acessa os próprios alunos.
- Nome de exercício único por personal. Um exercício em uso numa ficha não pode ser excluído.
- Fichas podem ser desativadas (`is_active`) sem perder o histórico. Uma ficha com treinos registrados não pode ser excluída, e um exercício com séries registradas não pode ser removido da ficha.
- Cada ficha tem de 1 a 20 séries por exercício. A carga registrada não pode ser negativa, e o número da série não passa do prescrito.
- Registrar a mesma série de novo corrige o valor, mantendo uma linha por série na sessão.
