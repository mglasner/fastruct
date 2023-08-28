"""Entry point de la aplicación."""
import typer
from commands.foundations.app import app as foundations_app
from commands.loads.app import app as loads_app
from config_db import config_database

app = typer.Typer()


def config_app():
    """App. Configuration."""
    app.add_typer(loads_app, name="l", help="💪 Loads Module")
    app.add_typer(foundations_app, name="f", help="🏢 Foundations Module")


if __name__ == "__main__":
    config_database()
    config_app()
    app()
