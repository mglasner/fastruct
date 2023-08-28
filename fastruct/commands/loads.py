"""Comandos para el módulo cargas."""
import csv
from pathlib import Path
from typing import Optional

import typer
from config_db import session_scope
from loads.queries import is_load_duplicated
from models.foundation import Foundation
from models.load import Load
from models.user_load import UserLoad
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()


@app.command(context_settings={"ignore_unknown_options": True})
def add(
    foundation_id: int,
    p: float,
    vx: float,
    vy: float,
    mx: float,
    my: float,
    name: Optional[str | None] = None,
) -> None:
    """Add a new load to the database.\n.

    Args:\n
        foundation_id (int): Foundation's ID to which the load is applied.\n
        p (float): Vertical force.\n
        vx (float): Horizontal force in the x direction.\n
        vy (float): Horizontal force in the y direction.\n
        mx (float): Moment around the x axis.\n
        my (float): Moment around the y axis.\n
        name (str | None): Optional name for the user load. Defaults to None.\n

    Returns:
        The function prints the added user load ID or a message if the load already exists.
    """
    user_load_dict = {
        "foundation_id": foundation_id,
        "name": name,
        "p": p,
        "vx": vx,
        "vy": vy,
        "mx": mx,
        "my": my,
    }

    with session_scope() as session:
        if not is_load_duplicated(session, user_load_dict):
            foundation = session.query(Foundation).filter_by(id=foundation_id).first()
            if foundation is None:
                print("Foundation not found")
                raise typer.Exit()

            user_load = UserLoad(**user_load_dict)
            session.add(user_load)
            session.flush()

            load = Load(
                foundation_id=foundation_id,
                user_load_id=user_load.id,
                p=p + foundation.weight() + foundation.ground_weight(),
                vx=vx,
                vy=vy,
                mx=mx + vy * foundation.lz + p * foundation.ey,
                my=my + vx * foundation.lz + p * foundation.ex,
            )
            session.add(load)
            print(f"{user_load.id=}")
        else:
            print("Load already exists for foundation.")


@app.command()
def add_from_csv(path: Path) -> None:
    """Generate user_loads and loads from a CSV file.\n.

    Assumes the CSV file has the following header format:\n
    id, name, p, vx, vy, mx, my, ex, ey\n

    Lines starting with '#' will be ignored. The first line is considered\n
    the title and is automatically skipped.\n

    Args:\n
        path (Path): Path to the CSV file.\n
    """
    if not path.is_file():
        raise ValueError("Path is not valid.")

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

            add(foundation_id, p, vx, vy, mx, my, name)

    print("File loaded")


@app.command(name="get")
def get_by_id(foundation_id: int):
    """Display load details for the requested foundation."""
    with session_scope() as session:
        foundation = session.query(Foundation).filter_by(id=foundation_id).first()
        table = Table("#", "ID", "NAME", "P", "Vx", "Vy", "Mx", "My")
        table.title = str(foundation)
        table.caption = "(value): loads at the f. CG and f. seal level"
        table.show_lines = True

        for i, (user_load, load) in enumerate(zip(foundation.user_loads, foundation.loads, strict=True), start=1):
            row = [
                f"{i:02}",
                f"{user_load.id}",
                user_load.name,
                f"{user_load.p :.1f} ({load.p:.1f})",
                f"{user_load.vx:.1f} ({load.vx:.1f})",
                f"{user_load.vy:.1f} ({load.vy:.1f})",
                f"{user_load.mx:.1f} ({load.mx:.1f})",
                f"{user_load.my:.1f} ({load.my:.1f})",
            ]

            table.add_row(*row)

    console.print(table)


@app.command()
def delete(user_load_id: int) -> None:
    """Delete a load from the database.\n

    This command deletes the user_load and load record with the specified ID from the database.\n

    Args:\n
        user_load_id (int): The ID of the user_load to delete.
    """
    with session_scope() as session:
        user_load = session.query(UserLoad).filter_by(id=user_load_id).first()
        if user_load is None:
            print("Load not found")
            raise typer.Exit()

        session.delete(user_load)

        print(f"Foundation with ID {user_load_id} has been deleted.")
