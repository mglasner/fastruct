"""Utility functions for beams app."""
import typer
from sqlalchemy.orm import Session

from fastruct.models.beam import Beam
from fastruct.models.project import Project


def add_beam(
    session: Session,
    length: float | None,
    name: str | None,
    description: str | None,
    coordinates: list[tuple[float, float]],
) -> tuple[Project, Beam]:
    """Add beam to database."""
    active_project = session.query(Project).filter_by(is_active=True).first()
    if active_project is None:
        typer.secho("No active project found")
        raise typer.Exit()

    beam = Beam(name=name, description=description, length=length, project_id=active_project.id)
    beam.set_coordinates(coordinates)
    session.add(beam)
    session.flush()

    return active_project, beam
