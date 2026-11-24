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
        """Cria personal, nutricionista, um aluno vinculado aos dois, exercicios e um plano."""
        from treinolog.auth import services as auth_services
        from treinolog.exercises import services as exercise_services
        from treinolog.nutrition import services as nutrition_services

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
        nutri = auth_services.register_user(
            name="Nutri Demo",
            email="nutri@treinolog.dev",
            password="demo1234",
            role="nutricionista",
        )
        auth_services.link_student(aluno, personal.invite_code)
        auth_services.link_student(aluno, nutri.invite_code)

        for name, group in [
            ("Supino reto", "Peito"),
            ("Agachamento livre", "Pernas"),
            ("Puxada frontal", "Costas"),
            ("Desenvolvimento com halteres", "Ombros"),
            ("Rosca direta", "Bíceps"),
        ]:
            exercise_services.create_exercise(personal, {"name": name, "muscle_group": group})

        nutrition_services.create_plan(nutri, {
            "student_id": aluno.id,
            "name": "Ganho de massa",
            "goal": "Ganhar 3 kg em 3 meses",
            "meals": [
                {"name": "Café da manhã", "time": "07:00",
                 "foods": "3 ovos mexidos, 2 fatias de pão integral e 1 banana", "kcal": 520},
                {"name": "Almoço", "time": "12:30",
                 "foods": "150 g de arroz, 100 g de feijão, 150 g de frango e salada", "kcal": 750},
                {"name": "Lanche", "time": "16:00",
                 "foods": "Iogurte natural com 30 g de aveia", "kcal": 300},
                {"name": "Jantar", "time": "20:00",
                 "foods": "150 g de batata-doce, 120 g de carne moída e legumes", "kcal": 620},
            ],
        })

        click.echo("Dados de exemplo criados (senha dos tres usuarios: demo1234).")
        click.echo(f"Codigo de convite do personal: {personal.invite_code}")
        click.echo(f"Codigo de convite da nutricionista: {nutri.invite_code}")
