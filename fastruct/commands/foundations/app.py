"""Foundations Commands."""
import csv
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import sqlalchemy as sa
import typer
from rich.console import Console

from fastruct.common.functions import check_not_none
from fastruct.config_db import session_scope
from fastruct.models.foundation import Foundation
from fastruct.models.project import Project
from fastruct.models.seal_load import SealLoad
from fastruct.models.user_load import UserLoad
from fastruct.plotting.foundations.plot import close_event, draw_foundation
from fastruct.queries.loads import is_load_duplicated
from fastruct.tables.foundations.analize import analize_table
from fastruct.tables.foundations.get import get_table
from fastruct.tables.foundations.get_loads import get_loads_table
from fastruct.tables.pagination import paginate_table

from .utils import get_max_value, stresses_and_percentajes_by_method

app = typer.Typer()
console = Console()


@app.command()
def add(
    lx: float = typer.Argument(help="Length of the foundation along the X-axis"),
    ly: float = typer.Argument(help="Length of the foundation along the Y-axis"),
    lz: float = typer.Argument(help="Length of the foundation along the Z-axis"),
    depth: float = typer.Option(
        None, help="Total depth of the foundation, measured from ground level to the foundation seal"
    ),
    ex: float = typer.Option(
        0, help="Eccentricity between the CG of the wall/column and the foundation CG along the X-axis"
    ),
    ey: float = typer.Option(
        0, help="Eccentricity between the CG of the wall/column and the foundation CG along the Y-axis"
    ),
    colx: float = typer.Option(0, help="Dimension of the wall/column above the foundation along the X-axis"),
    coly: float = typer.Option(0, help="Dimension of the wall/column above the foundation along the Y-axis"),
    name: str = typer.Option(None, help="Optional name for the foundation"),
    description: str = typer.Option(None, help="Optional description for the foundation"),
) -> None:
    """Add foundation."""
    if depth is None:
        depth = lz

    with session_scope() as session:
        active_project = session.query(Project).filter_by(is_active=True).first()
        foundation = Foundation(
            lx=lx,
            ly=ly,
            lz=lz,
            depth=depth,
            ex=ex,
            ey=ey,
            col_x=colx,
            col_y=coly,
            name=name,
            description=description,
            project_id=active_project.id,
        )
        session.add(foundation)
        session.flush()
        typer.secho(
            f"Foundation (id={foundation.id}) created succesfuly ({active_project.code})", fg=typer.colors.GREEN
        )


@app.command()
def get(
    id: int = typer.Option(None, help="ID of the foundation to retrieve. Leave empty to fetch all foundations."),
    rows_per_page: int = typer.Option(10, help="Number of records displayed per page", rich_help_panel="Format"),
) -> None:
    """Retrieve a single foundation by its ID, or all foundations from the database if no ID is provided."""
    with session_scope() as session:
        active_project = session.query(Project).filter_by(is_active=True).first()
        if id is None:
            foundations: list[Foundation] = (
                session.query(Foundation).filter_by(project_id=active_project.id).order_by(sa.desc("updated_at")).all()
            )
        else:
            foundation = session.query(Foundation).filter_by(id=id).filter_by(project_id=active_project.id).first()
            check_not_none(foundation, "foundation", str(id), active_project)
            foundations = [foundation]

        table, rows = get_table(foundations)
        paginate_table(table, rows, rows_per_page, get_table, foundations)


@app.command()
def update(
    id: int = typer.Argument(help="Foundation ID"),
    lx: float = typer.Argument(help="Length of the foundation along the X-axis"),
    ly: float = typer.Argument(help="Length of the foundation along the Y-axis"),
    lz: float = typer.Argument(help="Length of the foundation along the Z-axis"),
    depth: float = typer.Argument(
        help="Total depth of the foundation, measured from ground level to the foundation seal"
    ),
    ex: float = typer.Argument(
        help="Eccentricity between the CG of the wall/column and the foundation CG along the X-axis"
    ),
    ey: float = typer.Argument(
        help="Eccentricity between the CG of the wall/column and the foundation CG along the Y-axis"
    ),
    colx: float = typer.Argument(help="Dimension of the wall/column above the foundation along the X-axis"),
    coly: float = typer.Argument(help="Dimension of the wall/column above the foundation along the Y-axis"),
    name: str = typer.Option(None, help="Optional name for the foundation"),
    description: str = typer.Option(None, help="Optional description for the foundation"),
) -> None:
    """Update foundation."""
    with session_scope() as session:
        active_project = session.query(Project).filter_by(is_active=True).first()
        foundation = session.query(Foundation).filter_by(id=id).filter_by(project_id=active_project.id).first()
        check_not_none(foundation, "foundation", str(id), active_project)

        foundation.lx = lx
        foundation.ly = ly
        foundation.lz = lz
        foundation.depth = depth
        foundation.ex = ex
        foundation.ey = ey
        foundation.col_x = colx
        foundation.col_y = coly
        if name is not None:
            foundation.name = name
        if description is not None:
            foundation.description = description

        session.commit()

        for user_load, seal_load in zip(foundation.user_loads, foundation.seal_loads, strict=True):
            seal_load.p = user_load.p + foundation.weight() + foundation.ground_weight()
            seal_load.mx = user_load.mx + user_load.vy * foundation.lz + user_load.p * foundation.ey
            seal_load.my = user_load.my + user_load.vx * foundation.lz + user_load.p * foundation.ex

        print(foundation)


@app.command()
def delete(id: int = typer.Argument(help="Foundation ID")) -> None:
    """Delete foundation."""
    with session_scope() as session:
        active_project = session.query(Project).filter_by(is_active=True).first()
        foundation = session.query(Foundation).filter_by(id=id).filter_by(project_id=active_project.id).first()
        check_not_none(foundation, "foundation", str(id), active_project)

        session.delete(foundation)
        typer.secho(f"Foundation with ID {id} has been deleted ({active_project.code}).", fg=typer.colors.GREEN)


@app.command(name="add-load", context_settings={"ignore_unknown_options": True})
def add_load(
    id: int = typer.Argument(help="ID of the foundation to which the load will be added"),
    p: float = typer.Argument(help="Magnitude of the axial load"),
    vx: float = typer.Argument(help="Magnitude of the shear load in the X direction"),
    vy: float = typer.Argument(help="Magnitude of the shear load in the Y direction"),
    mx: float = typer.Argument(help="Magnitude of the moment about the X axis"),
    my: float = typer.Argument(help="Magnitude of the moment about the Y axis"),
    name: Optional[str] = typer.Option(None, help="Optional name for the load"),
) -> None:
    """Add a load to a foundation identified by its ID."""
    user_load_dict = {"foundation_id": id, "name": name, "p": p, "vx": vx, "vy": vy, "mx": mx, "my": my}

    with session_scope() as session:
        active_project = session.query(Project).filter_by(is_active=True).first()
        if not is_load_duplicated(session, user_load_dict):
            foundation = session.query(Foundation).filter_by(id=id).filter_by(project_id=active_project.id).first()
            check_not_none(foundation, "foundation", str(id), active_project)

            user_load = UserLoad(**user_load_dict)
            session.add(user_load)
            session.flush()

            load = SealLoad(
                foundation_id=id,
                user_load_id=user_load.id,
                p=p + foundation.weight() + foundation.ground_weight(),
                vx=vx,
                vy=vy,
                mx=mx + vy * foundation.lz + p * foundation.ey,
                my=my + vx * foundation.lz + p * foundation.ex,
            )
            session.add(load)
            typer.secho(f"Load added succesfuly ({active_project.code})", fg=typer.colors.GREEN)
        else:
            typer.secho(f"Load already exists for foundation (id: {id}) ({active_project.code})", fg=typer.colors.RED)


@app.command(name="add-loads-from-csv")
def add_loads_from_csv(path: Path = typer.Argument(help="Path to csv file")) -> None:
    """Add loads from csv file.

    - Format: id, name, p, vx, vy, mx, my

    - Lines starting with '#' will be ignored.

    - The first line is considered the title and is automatically skipped.

    - Empty lines are allowed.
    """
    if not path.is_file():
        typer.secho("Path is not valid.", fg=typer.colors.RED)
        raise typer.Exit()

    with open(path, newline="") as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # Skip title line
        for line in reader:
            # Skip empty lines or lines starting with '#'
            if not line or line[0].strip().startswith("#"):
                continue

            foundation_id = int(line[0])
            name = str(line[1]) if line[1] else None
            p = float(line[2])
            vx = float(line[3])
            vy = float(line[4])
            mx = float(line[5])
            my = float(line[6])

            add_load(foundation_id, p, vx, vy, mx, my, name)

    typer.secho("File loaded", fg=typer.colors.GREEN)


@app.command(name="get-loads")
def get_loads(
    id: int = typer.Argument(help="Foundation ID"),
    rows_per_page: int = typer.Option(10, help="Number of records displayed per page", rich_help_panel="Format"),
):
    """Display loads details for the requested foundation."""
    with session_scope() as session:
        active_project = session.query(Project).filter_by(is_active=True).first()
        foundation = session.query(Foundation).filter_by(id=id).filter_by(project_id=active_project.id).first()
        check_not_none(foundation, "foundation", str(id), active_project)
        table, rows = get_loads_table(foundation)
        paginate_table(table, rows, rows_per_page, get_loads_table, foundation)


@app.command(name="delete-load")
def delete_load(id: int = typer.Argument(help="Load ID")) -> None:
    """Delete foundation load."""
    with session_scope() as session:
        active_project = session.query(Project).filter_by(is_active=True).first()
        user_load = (
            session.query(UserLoad)
            .join(Foundation)
            .filter(sa.and_(UserLoad.id == id, Foundation.project_id == active_project.id))
            .first()
        )
        check_not_none(user_load, "load", str(id), active_project)
        session.delete(user_load)
        typer.secho(f"Load with ID {id} has been deleted ({active_project.code}).", fg=typer.colors.GREEN)


@app.command(name="analyze")
def analyze_stresses_and_lifts(
    id: int = typer.Argument(help="Foundation ID"),
    limit: float = typer.Option(
        None, help="Stress limit for highlighting. Results exceeding this limit will be highlighted in yellow."
    ),
    method: str = typer.Option(
        "bi-direction", help="Method for analysis. Options are 'bi-direction', 'one-direction', or 'compare'."
    ),
    order: str = typer.Option("percentage", help="Order results by 'stress' or 'percentage' of support."),
    color: bool = typer.Option(True, help="Whether to use colors in the results table."),
    show_loads: bool = typer.Option(True, help="Whether to display the loads applied to the foundation."),
    rows_per_page: int = typer.Option(10, help="Number of records displayed per page", rich_help_panel="Format"),
) -> None:
    """Analyze maximum stress and percentage of support for a foundation."""
    with session_scope() as session:
        active_project = session.query(Project).filter_by(is_active=True).first()
        foundation = session.query(Foundation).filter_by(id=id).filter_by(project_id=active_project.id).first()
        check_not_none(foundation, "foundation", str(id), active_project)

        stresses, percentajes = stresses_and_percentajes_by_method(foundation, method)  # type: ignore
        max_stress = get_max_value(stresses)
        table, rows = analize_table(
            foundation, limit, method, order, color, show_loads, stresses, percentajes, max_stress
        )
        paginate_table(
            table,
            rows,
            rows_per_page,
            analize_table,
            foundation,
            limit,
            method,
            order,
            color,
            show_loads,
            stresses,
            percentajes,
            max_stress,
        )


@app.command()
def plot(id: int = typer.Argument(help="Foundation ID")) -> None:
    """Plot foundation."""
    with session_scope() as session:
        active_project = session.query(Project).filter_by(is_active=True).first()
        foundation = session.query(Foundation).filter_by(id=id).filter_by(project_id=active_project.id).first()
        check_not_none(foundation, "foundation", str(id), active_project)
        plt.connect("key_press_event", close_event)
        typer.secho("Press 'q' to close foundation plot.", fg=typer.colors.GREEN)
        draw_foundation(foundation)


# @app.command()
# def flexural_design(id: int = typer.Argument(help="Foundation ID")) -> None:
#     """Flexural design of foundation."""
#     from foundations.design import get_ultimate_moments

#     with session_scope() as session:
#         active_project = session.query(Project).filter_by(is_active=True).first()
#         foundation = session.query(Foundation).filter_by(id=id).filter_by(project_id=active_project.id).first()
#         check_not_none(foundation, "foundation", str(id), active_project)
#         print(get_ultimate_moments(foundation))
