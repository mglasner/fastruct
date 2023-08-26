"""Comandos para el módulo analisis."""
import typer
from config_db import session_scope
from models.foundation import Foundation
from rich.console import Console
from rich.table import Table
from rich.text import Text

from .functions import get_stress, lifting_percentaje

app = typer.Typer()
console = Console()


@app.command(name="tl")
def tensiones_y_levantamientos(fundacion_id: int, verbose: bool = False):
    """Análisis de tensiones máximas y levantamientos."""
    with session_scope() as session:
        foundation = session.query(Foundation).filter_by(id=fundacion_id).first()
        table = Table("#", "NAME", "P", "Vx", "Vy", "Mx", "My", "σx max", r"%x", "σy max", r"%y")
        table.title = Text(str(foundation), style="black on white bold")
        table.show_lines = True

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

            row = [
                f"{i:02}",
                f"{load.user_load.name}",
                f"{load.p :.1f}",
                f"{load.vx:.1f}",
                f"{load.vy:.1f}",
                f"{load.mx:.1f}",
                f"{load.my:.1f}",
                sigma_x,
                percentaje_x,
                sigma_y,
                percentaje_y,
            ]

            table.add_row(*row)

    console.print(table)
