"""Common functions."""
from typing import Any

import typer

from fastruct.models.project import Project


def check_not_none(model: Any, model_name: str, active_project: Project) -> None:
    """Check if an entity instance exists and is linked to the active project.

    Args:
        entity: The entity instance to check.
        active_project (Project): The currently active Project instance.

    Raises:
        typer.Exit: Exits the command if the entity instance is not found.
    """
    if model is None:
        typer.secho(
            f"{model_name} not found in project {active_project.name} ({active_project.code})",
            fg=typer.colors.RED,
        )
        raise typer.Exit()
