"""Foundations Commands."""
from typing import Optional

import matplotlib.pyplot as plt
import sqlalchemy as sa
import typer
from rich.console import Console

from fastruct.common.functions import check_not_none
from fastruct.config_db import session_scope
from fastruct.models.foundation import Foundation
from fastruct.models.project import Project
from fastruct.plotting.foundations.plot import close_event, draw_foundation
from fastruct.tables.foundations.tables import analize_table, display_page, foundation_table, prepare_row

from .utils import get_max_value, stresses_and_percentajes_by_method

app = typer.Typer()
console = Console()


@app.command()
def add(
    lx: float,
    ly: float,
    lz: float,
    depth: Optional[float] = None,
    ex: Optional[float] = 0,
    ey: Optional[float] = 0,
    colx: Optional[float] = 0,
    coly: Optional[float] = 0,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> None:
    """Add a new foundation to the database.\n

    Args:\n
        lx (float): Width of the foundation in the x direction.\n
        ly (float): Width of the foundation in the y direction.\n
        lz (float): Height of the foundation in the z direction.\n
        depth (float | None): Depth of the foundation from the ground level to the seal of the foundation.\n
        ex (float | None, optional): Eccentricity in the x direction with respect to the center of gravity of the\n
                                     foundation. Defaults to 0.\n
        ey (float | None, optional): Eccentricity in the y direction with respect to the center of gravity of the\n
                                     foundation. Defaults to 0.\n
        colx (float | None): Width of the column over the foundation in x direction.\n
        coly (float | None): Width of the column over the foundation in y direction.\n
        name (str | None): Optional name for the foundation. Defaults to None. Max characters 32.\n
        description (str | None): Optional description for the foundation. Defaults to None. Max characters 128.\n
    """
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
def get(id: Optional[int] = None):
    """Get all foundations from database or the foundation with the provided id."""
    description_length = 29
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

        table = foundation_table()
        for foundation in foundations:
            description = None
            if foundation.description is not None:
                description = (
                    foundation.description
                    if len(foundation.description) <= description_length
                    else f"{foundation.description[:description_length]}..."
                )
            table.add_row(
                str(foundation.id),
                foundation.name,
                description,
                str(foundation.lx),
                str(foundation.ly),
                str(foundation.lz),
                str(foundation.depth),
                str(foundation.ex),
                str(foundation.ey),
                f"{foundation.col_x:.1f}x{foundation.col_y:.1f}",
                f"{foundation.area():.3f}",
                f"{foundation.volume():.3f}",
                f"{foundation.weight():.3f}",
            )
    console.print(table)


@app.command()
def update(
    id: int,
    lx: float,
    ly: float,
    lz: float,
    depth: float,
    ex: float,
    ey: float,
    colx: float,
    coly: float,
    name: Optional[str] = None,
    description: Optional[str] = None,
):
    """Update a foundation in the database.\n

    Args:\n
        id (int): The ID of the foundation to update.\n
        lx (float): Width of the foundation in the x direction.\n
        ly (float): Width of the foundation in the y direction.\n
        lz (float): Height of the foundation in the z direction.\n
        depth (float): Depth of the foundation from the ground level to the seal of the foundation.\n
        ex (float): Eccentricity in the x direction with respect to the center of gravity of the\n
                    foundation. Defaults to 0.\n
        ey (float): Eccentricity in the y direction with respect to the center of gravity of the\n
                    foundation. Defaults to 0.\n
        colx (float): Width of the column over the foundation in x direction.\n
        coly (float): Width of the column over the foundation in y direction.\n
        name (str | None): Optional name for the foundation. Defaults to None. Max characters 32.\n
        description (str | None): Optional description for the foundation. Defaults to None. Max characters 128.\n
    """
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

        for user_load, load in zip(foundation.user_loads, foundation.loads, strict=True):
            load.p = user_load.p + foundation.weight() + foundation.ground_weight()
            load.mx = user_load.mx + user_load.vy * foundation.lz + user_load.p * foundation.ey
            load.my = user_load.my + user_load.vx * foundation.lz + user_load.p * foundation.ex

        print(foundation)


@app.command()
def delete(foundation_id: int) -> None:
    """Delete a foundation from database.\n

    This command deletes the foundation record with the specified ID from the database.\n

    Args:\n
        foundation_id (int): The ID of the foundation to delete.
    """
    with session_scope() as session:
        active_project = session.query(Project).filter_by(is_active=True).first()
        foundation = (
            session.query(Foundation).filter_by(id=foundation_id).filter_by(project_id=active_project.id).first()
        )
        check_not_none(foundation, "foundation", str(foundation_id), active_project)

        session.delete(foundation)
        typer.secho(
            f"Foundation with ID {foundation_id} has been deleted ({active_project.code}).", fg=typer.colors.GREEN
        )


@app.command(name="analize")
def analyze_stresses_and_lifts(
    foundation_id: int,
    limit: float = typer.Option(None, help="Stress limit. Results exceeding this value will be highlighted in yellow"),
    method: str = typer.Option("bi-direction", help="bi-direction/one-direction/compare"),
    order: str = typer.Option(None, help="stress/percentaje"),
    color: bool = typer.Option(True, help="Use colors on results table", rich_help_panel="Format"),
    show_loads: bool = typer.Option(True, help="Show the loads applied over foundation", rich_help_panel="Format"),
    rows_per_page: int = typer.Option(10, help="Records per page", rich_help_panel="Format"),
) -> None:
    """Analyze maximum stress and support percentaje."""
    with session_scope() as session:
        active_project = session.query(Project).filter_by(is_active=True).first()
        foundation = (
            session.query(Foundation).filter_by(id=foundation_id).filter_by(project_id=active_project.id).first()
        )
        check_not_none(foundation, "foundation", str(foundation_id), active_project)

        stresses, percentajes = stresses_and_percentajes_by_method(foundation, method)  # type: ignore
        max_stress = get_max_value(stresses)

        loads = foundation.loads
        if order is not None:
            if order not in ("stress", "percentaje"):
                typer.secho("Order must be 'stress' or 'percentaje'", fg=typer.colors.RED)
                raise typer.Exit()

            data = list(zip(foundation.loads, stresses, percentajes, strict=True))
            if order == "stress":
                # Order desc by 'stress'
                data.sort(key=lambda x: (x[1] is None, x[1]), reverse=True)
            else:
                # Order asc by 'percentaje'
                data.sort(key=lambda x: x[2])

            loads, stresses, percentajes = zip(*data, strict=True)

        all_rows = []
        for i, (load, stress, percentaje) in enumerate(zip(loads, stresses, percentajes, strict=True), start=1):
            row = prepare_row(i, load, stress, percentaje, method, max_stress, limit, show_loads, color)  # type: ignore
            all_rows.append(row)

        table = analize_table(str(foundation), method, show_loads)  # type: ignore
        if rows_per_page is None:
            rows_per_page = 20

        num_pages = len(all_rows) // rows_per_page + (1 if len(all_rows) % rows_per_page else 0)
        for page in range(num_pages):
            start_idx = page * rows_per_page
            end_idx = start_idx + rows_per_page
            table = analize_table(str(foundation), method, show_loads)  # type: ignore
            display_page(start_idx, end_idx, all_rows, table)
            if page < num_pages - 1:
                user_input = input(f"Page {page+1}/{num_pages}, press Enter to watch next results, 'q' to quit... ")
                if user_input == "q":
                    break


@app.command()
def flexural_design(foundation_id: int) -> None:
    """Flexural design of foundation."""
    from foundations.design import get_ultimate_moments

    with session_scope() as session:
        active_project = session.query(Project).filter_by(is_active=True).first()
        foundation = (
            session.query(Foundation).filter_by(id=foundation_id).filter_by(project_id=active_project.id).first()
        )
        check_not_none(foundation, "foundation", str(foundation_id), active_project)
        print(get_ultimate_moments(foundation))


@app.command()
def plot(foundation_id: int) -> None:
    """Plot foundation."""
    with session_scope() as session:
        active_project = session.query(Project).filter_by(is_active=True).first()
        foundation = (
            session.query(Foundation).filter_by(id=foundation_id).filter_by(project_id=active_project.id).first()
        )
        check_not_none(foundation, "foundation", str(foundation_id), active_project)

        plt.connect("key_press_event", close_event)
        typer.secho("Press 'q' to close foundation plot.", fg=typer.colors.GREEN)
        draw_foundation(foundation)
