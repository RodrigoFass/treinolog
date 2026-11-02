import click

from treinolog.ext.db import db


def init_app(app):
    @app.cli.command("create-db")
    def create_db():
        """Cria as tabelas a partir dos modelos (atalho de desenvolvimento)."""
        db.create_all()
        click.echo("Tabelas criadas.")

    @app.cli.command("seed")
    def seed():
        """Cria um personal, um aluno vinculado e alguns exercicios de exemplo."""
        from treinolog.auth import services as auth_services
        from treinolog.exercises import services as exercise_services

        personal = auth_services.register_user(
            name="Personal Demo",
            email="personal@treinolog.dev",
            password="demo1234",
            role="personal",
        )
        aluno = auth_services.register_user(
            name="Aluno Demo",
            email="aluno@treinolog.dev",
            password="demo1234",
            role="aluno",
        )
        auth_services.link_student(aluno, personal.invite_code)

        for name, group in [
            ("Supino reto", "Peito"),
            ("Agachamento livre", "Pernas"),
            ("Puxada frontal", "Costas"),
            ("Desenvolvimento com halteres", "Ombros"),
            ("Rosca direta", "Biceps"),
        ]:
            exercise_services.create_exercise(personal, {"name": name, "muscle_group": group})

        click.echo("Dados de exemplo criados (senha dos dois usuarios: demo1234).")
        click.echo(f"Codigo de convite do personal: {personal.invite_code}")
