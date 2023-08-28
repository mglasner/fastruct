"""Foundations Commands."""
from typing import Optional

import sqlalchemy as sa
import typer
from config_db import session_scope
from foundations.analysis.bi_direction import bi_direction_analysis
from foundations.analysis.one_direction import one_direction_analysis
from foundations.tables import config_table, foundation_table
from models.foundation import Foundation
from rich.console import Console
from rich.text import Text

from .utils import data_by_method, get_max_value

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
        fundacion = Foundation(
            lx=lx, ly=ly, lz=lz, depth=depth, ex=ex, ey=ey, col_x=colx, col_y=coly, name=name, description=description
        )
        session.add(fundacion)
        session.flush()
        print(f"{fundacion.id=}")


@app.command()
def get(id: Optional[int] = None):
    """Get all foundations from database or the foundation with the provided id."""
    description_length = 29
    with session_scope() as session:
        if id is None:
            foundations: list[Foundation] = session.query(Foundation).order_by(sa.desc("updated_at")).all()
        else:
            foundation = session.query(Foundation).filter_by(id=id).first()
            if foundation is None:
                print("Foundation not found")
                raise typer.Exit()
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
        foundation = session.query(Foundation).filter_by(id=id).first()
        if foundation is None:
            print("Foundation not found")
            raise typer.Exit()

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
            load.mx = user_load.mx + user_load.vy * foundation.lz + user_load.p * user_load.ey
            load.my = user_load.my + user_load.vx * foundation.lz + user_load.p * user_load.ex

        print(foundation)


@app.command()
def delete(foundation_id: int) -> None:
    """Delete a foundation from the database.\n

    This command deletes the foundation record with the specified ID from the database.\n

    Args:\n
        foundation_id (int): The ID of the foundation to delete.
    """
    with session_scope() as session:
        foundation = session.query(Foundation).filter_by(id=foundation_id).first()
        if foundation is None:
            print("Foundation not found")
            raise typer.Exit()

        session.delete(foundation)

        print(f"Foundation with ID {foundation_id} has been deleted.")


@app.command(name="analize")
def analyze_stresses_and_lifts(
    foundation_id: int,
    method: Optional[str] = "bi-direction",
    limit: Optional[float] = None,
    no_loads: bool = False,
    no_color: bool = False,
) -> None:
    """Analyze maximum stresses and lifts.\n

    This function takes the ID of a foundation, fetches the foundation data and then\n
    computes the maximum stresses and lifts occurring in the foundation.\n

    Args:\n
        foundation_id (int): The ID of the foundation to analyze.\n
    """
    with session_scope() as session:
        foundation = session.query(Foundation).filter_by(id=foundation_id).first()
        if foundation is None:
            print("Foundation not found")
            raise typer.Exit()

        table = config_table(str(foundation), method, no_loads)  # type: ignore
        bi_stresses, bi_percentajes = bi_direction_analysis(foundation)
        one_stresses, one_percentajes = one_direction_analysis(foundation)
        all_stresses = [(s1, s2, s3) for s1, (s2, s3) in zip(bi_stresses, one_stresses, strict=True)]
        all_percentajes = [(p1, p2, p3) for p1, (p2, p3) in zip(bi_percentajes, one_percentajes, strict=True)]

        if method == "bi-direction":
            stresses, percentajes = bi_stresses, bi_percentajes

        elif method == "one-direction":
            stresses, percentajes = one_stresses, one_percentajes

        elif method == "compare":
            stresses, percentajes = all_stresses, all_percentajes
        else:
            print(f"Unkwnown method: {method}")
            raise typer.Exit()

        max_stress = get_max_value(stresses)
        for i, (load, stress, percentaje) in enumerate(
            zip(foundation.loads, stresses, percentajes, strict=True), start=1
        ):
            row = [
                Text(f"{i:02}", style="bold"),
                Text(f"{load.user_load.name}", style="bold") if load.user_load.name is not None else None,
            ]

            if not no_loads:
                row.extend(
                    [
                        Text(f"{load.p :.1f}", style="black"),
                        Text(f"{load.vx:.1f}", style="black"),
                        Text(f"{load.vy:.1f}", style="black"),
                        Text(f"{load.mx:.1f}", style="black"),
                        Text(f"{load.my:.1f}", style="black"),
                    ]
                )

            extra_data = data_by_method(stress, percentaje, method, max_stress, limit, no_color)  # type: ignore
            row.extend(extra_data)
            table.add_row(*row)

        console.print(table)
