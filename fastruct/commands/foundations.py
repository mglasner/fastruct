"""Foundations Commands."""
from typing import Optional

import typer
from config_db import session_scope
from models.foundation import Foundation
from rich.console import Console

from .utils import foundation_table

app = typer.Typer()
console = Console()


@app.command()
def add(
    lx: float,
    ly: float,
    lz: float,
    depth: Optional[float] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> None:
    """Add a new foundation to the database.\n.

    Args:\n
        lx (float): Width of the foundation in the x direction.\n
        ly (float): Width of the foundation in the y direction.\n
        lz (float): Height of the foundation in the z direction.\n
        depth (float | None): Depth of the foundation from the ground level to the seal of the foundation.\n
        name (str | None): Optional name for the foundation. Defaults to None. Max characters 32.\n
        description (str | None): Optional description for the foundation. Defaults to None. Max characters 128.\n
    """
    if depth is None:
        depth = lz

    with session_scope() as session:
        fundacion = Foundation(lx=lx, ly=ly, lz=lz, depth=depth, name=name, description=description)
        session.add(fundacion)
        session.flush()
        print(f"{fundacion.id=}")


@app.command()
def get():
    """List all the foundations in the database."""
    with session_scope() as session:
        foundations: list[Foundation] = session.query(Foundation).all()
        table = foundation_table()
        for foundation in foundations:
            description = None
            if foundation.description is not None:
                description = (
                    foundation.description if len(foundation.description) <= 29 else f"{foundation.description[:29]}..."
                )
            table.add_row(
                str(foundation.id),
                foundation.name,
                description,
                str(foundation.lx),
                str(foundation.ly),
                str(foundation.lz),
                str(foundation.depth),
                f"{foundation.area():.3f}",
                f"{foundation.volume():.3f}",
                f"{foundation.weight():.3f}",
            )
    console.print(table)


@app.command()
def get_by_id(foundation_id: int):
    """Foundation details."""
    with session_scope() as session:
        foundation = session.query(Foundation).filter_by(id=foundation_id).first()
        if foundation is None:
            print("Foundation not found")
            raise typer.Exit()

        table = foundation_table()
        table.add_row(
            str(foundation.id),
            foundation.name,
            foundation.description,
            str(foundation.lx),
            str(foundation.ly),
            str(foundation.lz),
            str(foundation.depth),
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
    name: Optional[str] = None,
    description: Optional[str] = None,
):
    """Update a foundation in the database.\n.

    Args:\n
        id (int): The ID of the foundation to update.\n
        lx (float): Width of the foundation in the x direction.\n
        ly (float): Width of the foundation in the y direction.\n
        lz (float): Height of the foundation in the z direction.\n
        depth (float): Depth of the foundation from the ground level to the seal of the foundation.\n
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
        if depth is not None:
            foundation.depth = depth
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
