"""Foundations Rich tables configuration module."""
from typing import Literal

from rich.table import Table
from rich.text import Text


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


def foundation_table() -> Table:
    """Crear una tabla para visualizar las fundaciones y determinar el factor de conversión de unidades.

    La tabla incluirá columnas para ID, Ancho, Largo, Alto, Volumen, y Peso, y se ajustará según la unidad especificada.

    Returns:
        Table: Tabla creada.
    """
    return Table(
        "F. ID",
        "Name",
        "Desc.",
        "Lx(m)",
        "Ly(m)",
        "Lz(m)",
        "Depth(m)",
        "Area(m²)",
        "Vol.(m³)",
        "Weight (t)",
    )
