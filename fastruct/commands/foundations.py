"""Foundations Commands."""
from typing import Literal, Optional

import sqlalchemy as sa
import typer
from config_db import session_scope
from foundations.analysis.bi_direction import bi_direction_analysis
from foundations.analysis.one_direction import one_direction_analysis
from foundations.tables import config_table, foundation_table
from models.foundation import Foundation
from rich.console import Console
from rich.text import Text

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
    col_x: Optional[float] = 0,
    col_y: Optional[float] = 0,
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
        col_x (float | None): Width of the column over the foundation in x direction.\n
        col_y (float | None): Width of the column over the foundation in y direction.\n
        name (str | None): Optional name for the foundation. Defaults to None. Max characters 32.\n
        description (str | None): Optional description for the foundation. Defaults to None. Max characters 128.\n
    """
    if depth is None:
        depth = lz

    with session_scope() as session:
        fundacion = Foundation(
            lx=lx, ly=ly, lz=lz, depth=depth, ex=ex, ey=ey, col_x=col_x, col_y=col_y, name=name, description=description
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
    col_x: float,
    col_y: float,
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
        col_x (float): Width of the column over the foundation in x direction.\n
        col_y (float): Width of the column over the foundation in y direction.\n
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
        foundation.col_x = col_x
        foundation.col_y = col_y
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
    foundation_id: int, method: Optional[str] = "bi-direction", no_loads: bool = False
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

        for i, (load, stress, percentaje) in enumerate(
            zip(foundation.loads, stresses, percentajes, strict=True), start=1
        ):
            row = [
                f"{i:02}",
                f"{load.user_load.name}" if load.user_load.name is not None else None,
            ]

            if not no_loads:
                row.extend(
                    [
                        f"{load.p :.1f}",
                        f"{load.vx:.1f}",
                        f"{load.vy:.1f}",
                        f"{load.mx:.1f}",
                        f"{load.my:.1f}",
                    ]
                )

            extra_data = data_by_method(stress, percentaje, method)  # type: ignore
            row.extend(extra_data)
            table.add_row(*row)

        console.print(table)


def data_by_method(
    stress: list[float], percentaje: list[float], method: Literal["bi-directional", "one-direction", "compare"]
) -> list[str]:
    """Generate row data by analysis method."""
    data = []
    if method == "bi-direction":
        data.extend(
            [
                f"{stress:.2f}" if stress is not None else "∞",
                f"{percentaje:.2f}",
            ]
        )
    elif method == "one-direction":
        stress_x, stress_y = stress
        percentaje_x, percentaje_y = percentaje
        data.extend(
            [
                f"{stress_x:.2f}" if stress_x is not None else "∞",
                f"{percentaje_x:.2f}",
                f"{stress_y:.2f}" if stress_y is not None else "∞",
                f"{percentaje_y:.2f}",
            ]
        )
    elif method == "compare":
        bi_stress, stress_x, stress_y = stress
        bi_percentaje, percentaje_x, percentaje_y = percentaje
        data.extend(
            [
                f"{bi_stress:.2f}" if bi_stress is not None else "∞",
                f"{bi_percentaje:.2f}",
                f"{stress_x:.2f}" if stress_x is not None else "∞",
                f"{percentaje_x:.2f}",
                f"{stress_y:.2f}" if stress_y is not None else "∞",
                f"{percentaje_y:.2f}",
            ]
        )

    return data

    # liftings = lifting_percentaje(foundation)
    # stresses = get_stress(foundation)
    # stress_max_total_x = max(stress[0] if stress[0] is not None else -1 for stress in stresses)
    # stress_max_total_y = max(stress[2] if stress[2] is not None else -1 for stress in stresses)

    # percentaje_min_total_x = min(percentaje[0] for percentaje in liftings)
    # percentaje_min_total_y = min(percentaje[1] for percentaje in liftings)
    # percentaje_100 = 100

    # for i, (load, (stress_max_x, _, stress_max_y, _), (percentaje_x, percentaje_y)) in enumerate(
    #     zip(foundation.loads, stresses, liftings, strict=True), start=1
    # ):
    #     sigma_x = (
    #         (f"{stress_max_x:.2f}" if stress_max_x is not None else "∞")
    #         if stress_max_x != stress_max_total_x
    #         else Text(f"{stress_max_x:.2f}", style="red")
    #     )

    #     sigma_y = (
    #         (f"{stress_max_y:.2f}" if stress_max_y is not None else "∞")
    #         if stress_max_y != stress_max_total_y
    #         else Text(f"{stress_max_y:.2f}", style="red")
    #     )

    #     percentaje_x = (  # noqa: PLW2901
    #         Text(f"{percentaje_x:.2f}", style="blue")
    #         if percentaje_x == percentaje_min_total_x and percentaje_min_total_x != percentaje_100
    #         else f"{percentaje_x:.2f}"
    #     )

    #     percentaje_y = (  # noqa: PLW2901
    #         Text(f"{percentaje_y:.2f}", style="blue")
    #         if percentaje_y == percentaje_min_total_y and percentaje_min_total_y != percentaje_100
    #         else f"{percentaje_y:.2f}"
    #     )

    #     bi_directional_max_stress, bi_directional_percentaje = get_bi_directional_percentaje_and_stress(
    #         foundation, load
    #     )

    #     row = [
    #         f"{i:02}",
    #         f"{load.user_load.name}",
    #         f"{load.p :.1f}",
    #         f"{load.vx:.1f}",
    #         f"{load.vy:.1f}",
    #         f"{load.mx:.1f}",
    #         f"{load.my:.1f}",
    #         # sigma_x,
    #         # percentaje_x,
    #         # sigma_y,
    #         # percentaje_y,
    #         f"{bi_directional_max_stress:.2f}" if bi_directional_max_stress is not None else "∞",
    #         f"{bi_directional_percentaje:.2f}",
    #     ]

    #     table.add_row(*row)
