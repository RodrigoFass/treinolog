import logging
import os
from logging.handlers import RotatingFileHandler

FORMATO = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def init_app(app):
    nivel = app.config.get("LOG_LEVEL", "INFO")
    formatter = logging.Formatter(FORMATO)

    # Log no console (aparece no terminal do flask run)
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    handlers = [console]

    # Log em arquivo, com rotacao para o arquivo nao crescer sem limite
    pasta = app.config.get("LOG_DIR")
    if pasta:
        os.makedirs(pasta, exist_ok=True)
        arquivo = RotatingFileHandler(
            os.path.join(pasta, "treinolog.log"),
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        arquivo.setFormatter(formatter)
        handlers.append(arquivo)

    # O app.logger do Flask se chama "treinolog" (nome do pacote), entao
    # os loggers dos modulos (treinolog.auth.services etc.) herdam dele
    app.logger.handlers = handlers
    app.logger.setLevel(nivel)
    app.logger.propagate = False
