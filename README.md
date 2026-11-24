# TreinoLog

Aplicação web em que o personal trainer monta as fichas de treino, o nutricionista monta o plano alimentar e o aluno registra, pelo celular, a carga de cada série, as refeições do dia e o peso. Uma ofensiva no estilo do Duolingo, com calendário, medalhas e conquistas, incentiva o aluno a não falhar.

**Integrantes:** Rodrigo Fassarella Leite e Pedro Henrique Meneghelli

## Arquitetura

Cliente-servidor em três camadas, a mesma do TaskFlow:

| Camada | Tecnologias |
|---|---|
| Frontend (`frontend/`) | Vue 3, Vite, Vue Router, Pinia, Axios, Chart.js, Bulma |
| Backend (`backend/`) | Python 3.12, Flask (Application Factory + blueprints), Flask-SQLAlchemy, Flask-Migrate, Flask-JWT-Extended, Pydantic |
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
│   ├── utils.py            # leitura e validação do JSON (validate_json)
│   ├── ext/                # db, jwt, errors, cli, logs
│   ├── auth/               # users: cadastro, login, vínculo, painel
│   ├── exercises/          # exercises: catálogo do personal
│   ├── workouts/           # workouts + workout_exercises: fichas
│   ├── sessions/           # workout_sessions + set_logs: treinos e evolução
│   ├── nutrition/          # meal_plans + meals + meal_logs + weight_logs: alimentação e peso
│   └── achievements/       # ofensiva, calendário, medalhas e conquistas (calculados)
└── tests/                  # PyTest + pytest-flask
```

Cada módulo de domínio tem `models.py` (tabelas), `schemas.py` (validação com Pydantic), `services.py` (regras de negócio) e `routes.py` (blueprint da API).

## Identidade visual

- **Logo:** anel de progresso com as três cores do app e um "T" no meio (`frontend/src/components/AppLogo.vue`, também usado como favicon).
- **Paleta:** rosa para treino, turquesa para alimentação, laranja para a ofensiva e violeta como cor principal. Cada cor tem uma versão para o tema claro e outra para o escuro (`frontend/src/style.css`).
- **Tema claro e escuro:** o botão de sol/lua na barra troca o tema. A escolha fica salva no navegador; sem escolha, o app segue o tema do sistema.
- **Fontes:** Space Grotesk nos títulos e Inter no texto, empacotadas com o app (`@fontsource`).

Os logs saem no console e em `backend/logs/treinolog.log` (configurável por `LOG_LEVEL` e `LOG_DIR` no `.env`).

## Como rodar

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -e ".[dev,test]"
copy .env.example .env          # ajuste SECRET_KEY e JWT_SECRET_KEY
copy .env .env.dev              # o invoke run usa o .env.dev
flask --app app db upgrade      # cria as tabelas
flask --app app seed            # opcional: personal, nutricionista e aluno de demonstração
invoke run                      # API em http://127.0.0.1:5000
```

Contas criadas pelo `seed`: `personal@treinolog.dev`, `nutri@treinolog.dev` e `aluno@treinolog.dev`, todas com a senha `demo1234`. O aluno já vem vinculado aos dois profissionais e com um plano alimentar.

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
| POST | `/api/auth/link` | aluno (código do personal ou do nutricionista) | RF02 / RF10 |
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
| GET | `/api/nutrition/patients` | nutricionista | RF14 |
| GET/POST | `/api/nutrition/plans` | nutricionista (GET: aluno vê o plano ativo) | RF11 |
| GET/PUT/DELETE | `/api/nutrition/plans/<id>` | nutricionista (GET: aluno dono também) | RF11 |
| GET | `/api/nutrition/today` | aluno | RF12 |
| PUT | `/api/nutrition/meals/<id>/check` | aluno | RF12 |
| GET | `/api/nutrition/adherence` | nutricionista, aluno | RF12 |
| GET/POST | `/api/nutrition/weights` | nutricionista (GET), aluno | RF13 |
| GET | `/api/achievements` | todos | RF15 |

O personal e o nutricionista consultam os dados de um aluno passando `?student_id=`.

## Regras de negócio implementadas

- Senha guardada só como hash (`werkzeug.security`).
- Cada rota verifica o perfil e o dono do recurso. O aluno só acessa os próprios dados, e o personal só acessa os próprios alunos.
- Nome de exercício único por personal. Um exercício em uso numa ficha não pode ser excluído.
- Fichas podem ser desativadas (`is_active`) sem perder o histórico. Uma ficha com treinos registrados não pode ser excluída, e um exercício com séries registradas não pode ser removido da ficha.
- Cada ficha tem de 1 a 20 séries por exercício. A carga registrada não pode ser negativa, e o número da série não passa do prescrito.
- Registrar a mesma série de novo corrige o valor, mantendo uma linha por série na sessão.
- O aluno pode ter um personal e um nutricionista; o código de convite diz qual dos dois ele está vinculando.
- O aluno segue um plano alimentar por vez: um plano novo desativa o anterior, e o histórico fica. Plano com refeições já marcadas não pode ser excluído nem ter as refeições trocadas.
- Uma refeição só pode ser marcada uma vez por dia, e não dá para marcar um dia que ainda não chegou. O peso tem um registro por dia (registrar de novo corrige).
- **Ofensiva:** um dia conta quando o aluno registra um treino com pelo menos uma série ou marca todas as refeições do plano. Hoje sem atividade ainda não quebra a ofensiva.
- **Medalhas de tempo sem falha:** treino (1, 4 e 12 semanas seguidas com pelo menos 3 treinos) e dieta (7, 30 e 90 dias seguidos com todas as refeições), em bronze, prata e ouro.
