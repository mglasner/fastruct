"""Beams Commands."""
import matplotlib.pyplot as plt
import numpy as np
import typer
from shapely.geometry import Point, Polygon

from fastruct.analysis.interaction.interaction_2d import get_curve2d
from fastruct.common.functions import check_not_none
from fastruct.config_db import session_scope
from fastruct.models.beam import Beam
from fastruct.models.project import Project
from fastruct.plotting.curve2d import plot_curve2d
from fastruct.plotting.utils import close_event

app = typer.Typer()


@app.command()
def add_rectangular(
    width: float = typer.Argument(help="Width of the rectangular beam"),
    height: float = typer.Argument(help="Height of the rectangular beam"),
    length: float = typer.Option(None, help="Length of the beam"),
    name: str = typer.Option(None, help="Optional name for the foundation"),
    description: str = typer.Option(None, help="Optional description for the foundation"),
) -> None:
    """Add rectangular cross sectional beam."""
    if width <= 0 or height <= 0:
        typer.secho("width and height must be positive", fg=typer.colors.RED)
        raise typer.Exit()

    if length is not None and length <= 0:
        typer.secho("length must be positive", fg=typer.colors.RED)
        raise typer.Exit()

    coordinates = [[0, 0], [width, 0], [width, height], [0, height], [0, 0]]
    with session_scope() as session:
        active_project = session.query(Project).filter_by(is_active=True).first()
        beam = Beam(name=name, description=description, length=length, project_id=active_project.id)
        beam.set_coordinates(coordinates)
        session.add(beam)
        session.flush()
        typer.secho(f"Beam (id={beam.id}) created succesfuly ({active_project.code})", fg=typer.colors.GREEN)


@app.command()
def add_reinforced_bar(
    id: int = typer.Argument(help="Beam ID"),
    x: float = typer.Argument(help="X coordinate"),
    y: float = typer.Argument(help="Y coordinate"),
    diameter: float = typer.Argument(help="bar diameter"),
    fy: float = typer.Option(42000, help="bar's yield stress (Fy)"),
    e: float = typer.Option(21000000, help="Bar's elasticity module (E)"),
) -> None:
    """Add 1 reinforced bar to beam."""
    with session_scope() as session:
        active_project = session.query(Project).filter_by(is_active=True).first()
        beam = session.query(Beam).filter_by(id=id).filter_by(project_id=active_project.id).first()
        check_not_none(beam, "beam", str(id), active_project)
        polygon = Polygon(beam.get_coordinates())
        point = Point(x, y)
        if not point.within(polygon):
            typer.secho(f"Bar is outside concrete section {id=}", fg=typer.colors.RED)
            raise typer.Exit()

        bars = beam.get_reinforced_bars()
        bars.append([x, y, diameter, fy, e])
        beam.set_reinforced_bars(bars)
        typer.secho(f"Reinforced bar added succesfuly (id={beam.id}) ({active_project.code})", fg=typer.colors.GREEN)


@app.command()
def plot2d(id: int = typer.Argument(help="Beam ID")) -> None:
    """Plot MP interaction 2d curve."""
    with session_scope() as session:
        active_project = session.query(Project).filter_by(is_active=True).first()
        beam = session.query(Beam).filter_by(id=id).filter_by(project_id=active_project.id).first()
        check_not_none(beam, "beam", str(id), active_project)
        plt.connect("key_press_event", close_event)
        typer.secho("Press 'q' to close foundation plot.", fg=typer.colors.GREEN)
        mp, reduction_factors = get_curve2d(np.array(beam.get_coordinates()), np.array(beam.get_reinforced_bars()))
        plot_curve2d(mp, np.array(beam.get_coordinates()), np.array(beam.get_reinforced_bars()))
