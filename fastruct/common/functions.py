"""Common functions."""
from typing import Any

import typer

from fastruct.models.project import Project


def check_not_none(model: Any, model_name: str, instance_name: str, active_project: Project) -> None:
    """Check if an entity instance exists and is linked to the active project.

    This function checks if a specified entity instance exists and if it is associated
    with the currently active project. If the entity instance is not found, it will print
    an error message and exit the command.

    Args:
        model (Any): The entity instance to check. This can be any SQLAlchemy model.
        model_name (str): The name of the entity type (e.g., 'Foundation', 'Project').
        instance_name (str): A descriptive name or identifier for the entity instance.
        active_project (Project): The currently active Project instance.

    Raises:
        typer.Exit: Exits the command if the entity instance is not found or not associated
                    with the active project.

    Examples:
        >>> check_not_none(foundation, 'Foundation', 'Foundation1', active_project)
        If foundation is None:
            prints "Foundation (Foundation1) not found in project 'ProjectName' (ProjectCode)"
            and exits the command.
    """
    if model is None:
        typer.secho(
            f"{model_name} ({instance_name}) not found in project '{active_project.name}' ({active_project.code})",
            fg=typer.colors.RED,
        )
        raise typer.Exit()
