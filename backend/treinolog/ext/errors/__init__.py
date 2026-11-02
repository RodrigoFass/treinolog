from werkzeug.exceptions import HTTPException


def init_app(app):
    # A API sempre responde erro em JSON, nunca a pagina HTML padrao do Flask
    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return {"erro": error.description}, error.code
