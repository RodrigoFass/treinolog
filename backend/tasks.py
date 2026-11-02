import os

from dotenv import load_dotenv
from invoke import task


def _load_env(environment):
    load_dotenv(".env.prod" if environment == "prod" else ".env.dev")


@task
def install(c):
    """Instala o projeto em modo editavel com dependencias de desenvolvimento e teste."""
    c.run('pip install -e ".[dev,test]"', echo=True)


@task
def run(c, environment="dev"):
    """Executa a API Flask (invoke run --environment prod)."""
    _load_env(environment)
    debug = "--debug" if os.getenv("FLASK_DEBUG") == "1" else ""
    c.run(f"flask --app app run {debug}", echo=True)


@task
def db_upgrade(c, environment="dev"):
    """Aplica as migracoes no banco configurado."""
    _load_env(environment)
    c.run("flask --app app db upgrade", echo=True)


@task
def seed(c):
    """Cria dados de exemplo no banco de desenvolvimento."""
    _load_env("dev")
    c.run("flask --app app seed", echo=True)


@task
def test(c):
    """Executa os testes automatizados."""
    c.run("pytest tests -v", echo=True)


@task
def cov(c):
    """Executa os testes com relatorio de cobertura."""
    c.run("pytest tests --cov=treinolog", echo=True)


@task
def lint(c):
    """Executa a verificacao de estilo com flake8."""
    c.run("flake8 treinolog tests --max-line-length 100", echo=True)


@task
def format(c):
    """Formata o codigo utilizando o Black."""
    c.run("black treinolog tests --line-length 100", echo=True)
