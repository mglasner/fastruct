"""Analysis Commands"""
from typing import Literal, Optional

import typer
from config_db import session_scope
from models.foundation import Foundation
from rich.console import Console
from rich.table import Table
from rich.text import Text

from .functions import get_bi_directional_percentaje_and_stress, get_stress, lifting_percentaje

app = typer.Typer()
console = Console()


@app.command(name="run")
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
        table = config_table(str(foundation), method, no_loads)  # type: ignore

        liftings = lifting_percentaje(foundation)
        stresses = get_stress(foundation)
        stress_max_total_x = max(stress[0] if stress[0] is not None else -1 for stress in stresses)
        stress_max_total_y = max(stress[2] if stress[2] is not None else -1 for stress in stresses)

        percentaje_min_total_x = min(percentaje[0] for percentaje in liftings)
        percentaje_min_total_y = min(percentaje[1] for percentaje in liftings)
        percentaje_100 = 100

        for i, (load, (stress_max_x, _, stress_max_y, _), (percentaje_x, percentaje_y)) in enumerate(
            zip(foundation.loads, stresses, liftings, strict=True), start=1
        ):
            sigma_x = (
                (f"{stress_max_x:.2f}" if stress_max_x is not None else "∞")
                if stress_max_x != stress_max_total_x
                else Text(f"{stress_max_x:.2f}", style="red")
            )

            sigma_y = (
                (f"{stress_max_y:.2f}" if stress_max_y is not None else "∞")
                if stress_max_y != stress_max_total_y
                else Text(f"{stress_max_y:.2f}", style="red")
            )

            percentaje_x = (  # noqa: PLW2901
                Text(f"{percentaje_x:.2f}", style="blue")
                if percentaje_x == percentaje_min_total_x and percentaje_min_total_x != percentaje_100
                else f"{percentaje_x:.2f}"
            )

            percentaje_y = (  # noqa: PLW2901
                Text(f"{percentaje_y:.2f}", style="blue")
                if percentaje_y == percentaje_min_total_y and percentaje_min_total_y != percentaje_100
                else f"{percentaje_y:.2f}"
            )

            bi_directional_max_stress, bi_directional_percentaje = get_bi_directional_percentaje_and_stress(
                foundation, load
            )

            row = [
                f"{i:02}",
                f"{load.user_load.name}",
                f"{load.p :.1f}",
                f"{load.vx:.1f}",
                f"{load.vy:.1f}",
                f"{load.mx:.1f}",
                f"{load.my:.1f}",
                # sigma_x,
                # percentaje_x,
                # sigma_y,
                # percentaje_y,
                f"{bi_directional_max_stress:.2f}" if bi_directional_max_stress is not None else "∞",
                f"{bi_directional_percentaje:.2f}",
            ]

            table.add_row(*row)

    console.print(table)


def config_table(title: str, method: Literal["bi-directional", "one-direction", "compare"], no_loads: bool) -> Table:
    """Table configuration."""
    columns = ["#", "NAME"]
    if not no_loads:
        columns.extend(["P", "Vx", "Vy", "Mx", "My"])

    if method == "bi-directional":
        columns.extend(["σ (ton/m²)", "%"])

    elif method == "one-direction":
        columns.extend(["σx max", r"%x", "σy max", r"%y"])

    elif method == "compare":
        columns.extend(["σx max", r"%x", "σy max", r"%y", "σ (ton/m²)", "%"])

    table = Table(*columns)
    table.title = Text(title, style="black on white bold")
    table.show_lines = True

    return table
