import logging

from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

logger = logging.getLogger("treinolog.errors")

# Traducao das mensagens mais comuns do Pydantic
MENSAGENS = {
    "missing": "e obrigatorio",
    "string_too_short": "nao pode ficar vazio",
    "string_too_long": "e maior que o permitido",
    "int_type": "deve ser um numero inteiro",
    "int_parsing": "deve ser um numero inteiro",
    "float_type": "deve ser numerico",
    "float_parsing": "deve ser numerico",
    "bool_type": "deve ser verdadeiro ou falso",
    "bool_parsing": "deve ser verdadeiro ou falso",
    "greater_than_equal": "esta abaixo do minimo permitido",
    "less_than_equal": "esta acima do maximo permitido",
    "literal_error": "tem um valor invalido",
    "string_type": "deve ser texto",
    "list_type": "deve ser uma lista",
    "model_type": "deve ser um objeto",
    "datetime_from_date_parsing": "deve estar no formato AAAA-MM-DDTHH:MM",
    "datetime_parsing": "deve estar no formato AAAA-MM-DDTHH:MM",
    "datetime_type": "deve estar no formato AAAA-MM-DDTHH:MM",
}


def mensagem_validacao(error: ValidationError) -> str:
    primeiro = error.errors()[0]
    campo = ".".join(str(parte) for parte in primeiro["loc"]) or "corpo"
    texto = MENSAGENS.get(primeiro["type"], primeiro["msg"])
    return f"Campo '{campo}' {texto}"


def init_app(app):
    # A API sempre responde erro em JSON, nunca a pagina HTML padrao do Flask
    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        if error.code >= 500:
            logger.error("Erro %s: %s", error.code, error.description)
        else:
            logger.warning("Erro %s: %s", error.code, error.description)
        return {"erro": error.description}, error.code

    # Erros de validacao dos schemas (Pydantic) viram 400
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        mensagem = mensagem_validacao(error)
        logger.warning("Erro de validacao: %s", mensagem)
        return {"erro": mensagem}, 400

    # Qualquer outro erro inesperado: registra o traceback e responde 500
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        logger.exception("Erro inesperado: %s", error)
        return {"erro": "Erro interno no servidor"}, 500
