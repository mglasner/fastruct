"""Project Commands."""
from typing import Optional

import sqlalchemy as sa
import typer
from rich.console import Console
from rich.text import Text

from fastruct.config_db import session_scope
from fastruct.models.project import Project
from fastruct.projects.tables import projects_table

app = typer.Typer()
console = Console()


@app.command()
def new(name: str, code: str, description: Optional[str] = None, activate: Optional[bool] = True) -> None:
    """Create new project."""
    with session_scope() as session:
        if activate:
            stmt = sa.update(Project).values(is_active=False)
            session.execute(stmt)

        project = Project(name=name, code=code, description=description, is_active=activate)
        session.add(project)
        session.flush()
        typer.secho(f"Project {name} created{' and activated' if activate else ''} succesfuly", fg=typer.colors.GREEN)


@app.command()
def get():
    """Get list of projects."""
    table = projects_table()
    with session_scope() as session:
        projects = session.query(Project).all()
        for i, project in enumerate(projects, start=1):
            name = Text(project.name, style="green") if project.is_active else project.name
            table.add_row(f"{i:02}", f"{project.id}", name, project.code, project.description)

    console.print(table)


@app.command()
def delete(project_id: int) -> None:
    """Delete project from database.\n

    Args:\n
        project_id (int): The ID of the project to delete.
    """
    with session_scope() as session:
        project = session.query(Project).filter_by(id=project_id).first()
        if project is None:
            typer.secho("Project not found", fg=typer.colors.RED)
            raise typer.Exit()

        session.delete(project)
        typer.secho(f"Project with ID {project_id} has been deleted.", fg=typer.colors.GREEN)
