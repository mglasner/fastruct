"""Entry point de la aplicación."""
import typer

from fastruct.commands.beams.app import app as beams_app
from fastruct.commands.foundations.app import app as foundations_app
from fastruct.commands.projects.app import app as projects_app
from fastruct.config_db import config_database

app = typer.Typer(pretty_exceptions_enable=False)


def config_app():
    """App. Configuration."""
    app.add_typer(projects_app, name="p", help="📂 Projects")
    app.add_typer(foundations_app, name="f", help="🏢 Foundations")
    app.add_typer(beams_app, name="b", help="🏢 Beams")


def main():
    """Entrypoint function."""
    config_database()
    config_app()
    app()


main()
