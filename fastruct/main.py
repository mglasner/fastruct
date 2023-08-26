"""Entry point de la aplicación."""
import typer
from commands.analysis.app import app as analysis_app
from commands.foundations import app as foundations_app
from commands.loads import app as loads_app
from config_db import config_database

app = typer.Typer()


def config_app():
    """App. Configuration."""
    app.add_typer(analysis_app, name="a", help="🔢 Analysis related commands")
    app.add_typer(loads_app, name="l", help="💪 Loads related functions")
    app.add_typer(foundations_app, name="f", help="🏢 Foundations related functions")


if __name__ == "__main__":
    config_database()
    config_app()
    app()
