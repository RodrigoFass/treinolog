import os
from datetime import timedelta

from dotenv import load_dotenv

# Carrega o arquivo .env (se existir) antes de ler as variaveis de ambiente
load_dotenv()


# === Configuracao base (comum a todos os ambientes) ===
class DefaultConfig:
    DEBUG = False
    TESTING = False
    ENV = "default"

    SECRET_KEY = os.getenv("SECRET_KEY", "chave-padrao-insegura-troque-em-producao")

    # RNF07: o banco e trocado so por configuracao (DATABASE_URL)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///treinolog.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # RNF03: autenticacao da API por token JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-chave-padrao-insegura-troque-em-producao")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)

    # Logging: nivel e pasta onde fica o arquivo de log
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = os.getenv("LOG_DIR", "logs")


class DevelopmentConfig(DefaultConfig):
    DEBUG = True
    ENV = "development"


class TestingConfig(DefaultConfig):
    TESTING = True
    ENV = "testing"
    # Nos testes o PyTest usa SQLite em memoria
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # Nos testes nao precisa gravar log em arquivo
    LOG_DIR = None


class ProductionConfig(DefaultConfig):
    DEBUG = False
    ENV = "production"
    # Em producao: DATABASE_URL=mysql+pymysql://usuario:senha@host/treinolog?charset=utf8mb4


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DefaultConfig,
}
