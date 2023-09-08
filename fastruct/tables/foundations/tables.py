"""Foundations Rich tables configuration module."""
from typing import Any, Literal

from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()
PERCENTAJE_0 = 0
PERCENTAJE_80 = 80
PERCENTAJE_100 = 100

MAX_STRESS_COLOR = "red"
LIMIT_STRESS_COLOR = "yellow"
MIN_PERCENTAJE_COLOR = "blue"


def analize_table(title: str, method: Literal["bi-directional", "one-direction", "compare"], loads: bool) -> Table:
    """Table configuration."""
    columns = ["#", "NAME"]
    if loads:
        columns.extend(["P", "Vx", "Vy", "Mx", "My"])

    if method == "bi-direction":
        columns.extend(["σ (ton/m²)", "%"])

    elif method == "one-direction":
        columns.extend(["σx max", r"%x", "σy max", r"%y"])

    elif method == "compare":
        columns.extend(["σ (ton/m²)", "%", "σx max", r"%x", "σy max", r"%y"])

    table = Table(*columns)
    table.title = Text(title, style="black on white bold")
    table.show_lines = True

    return table


def format_rows(
    stress: list[float],
    percentaje: list[float],
    method: Literal["bi-directional", "one-direction", "compare"],
    max_stress: float,
    limit_stress: float | None = None,
    color: bool = True,
) -> list[str | Text]:
    """Generate row data by analysis method."""
    if limit_stress is None:
        limit_stress = max_stress

    if color:
        max_stress_color = "red"
        limit_stress_color = "yellow"
        min_percentaje_color = "blue"

    else:
        max_stress_color = ""
        limit_stress_color = ""
        min_percentaje_color = ""

    def format_stress(s: float) -> str | Text:
        if s == max_stress:
            return Text(f"{s:.2f}", style=f"{max_stress_color} italic bold")
        elif limit_stress <= s < max_stress:
            return Text(f"{s:.2f}", style=f"{limit_stress_color} italic")
        elif s < limit_stress:
            return Text(f"{s:.2f}", style="italic")
        else:
            return f"{s:.2f}"

    def format_percentaje(p: float) -> str | Text:  # noqa: PLR0911
        if p == PERCENTAJE_0:
            return Text(f"{p:.0f}%", style=f"{min_percentaje_color} bold")
        elif p < PERCENTAJE_80:
            return Text(f"{p:.0f}%", style="bold")
        elif p <= PERCENTAJE_100:
            return Text(f"{p:.0f}%", style="")
        else:
            return f"{p:.2f}"

    data = []

    if method == "bi-direction":
        data.extend(
            [format_stress(stress) if stress is not None else "∞", format_percentaje(percentaje)]  # type: ignore
        )
    elif method == "one-direction":
        stress_x, stress_y = stress
        percentaje_x, percentaje_y = percentaje
        data.extend(
            [
                format_stress(stress_x) if stress_x is not None else "∞",
                format_percentaje(percentaje_x),
                format_stress(stress_y) if stress_y is not None else "∞",
                format_percentaje(percentaje_y),
            ]
        )
    elif method == "compare":
        bi_stress, stress_x, stress_y = stress
        bi_percentaje, percentaje_x, percentaje_y = percentaje
        data.extend(
            [
                format_stress(bi_stress) if bi_stress is not None else "∞",
                format_percentaje(bi_percentaje),
                format_stress(stress_x) if stress_x is not None else "∞",
                format_percentaje(percentaje_x),
                format_stress(stress_y) if stress_y is not None else "∞",
                format_percentaje(percentaje_y),
            ]
        )

    return data


def prepare_row(
    i: int,
    load,
    stress: float,
    percentaje: float,
    method: Literal["bi-directional", "one-direction", "compare"],
    max_stress: float,
    limit: float | None,
    show_loads: bool,
    color: bool,
) -> tuple[Text]:
    """Prepare a single row for the output table.

    This function takes various parameters like index, load, stress, percentage, etc.,
    to prepare a single row for the table that will be displayed. The row includes
    the index, load details, stress, and percentage based on the method specified.

    Args:
        i (int): The index of the row.
        load: The load object containing user_load and other attributes.
        stress (float): The stress value for the current load.
        percentaje (float): The percentage value for the current load.
        method (str): The analysis method ("bi-direction", "one-direction", "compare").
        max_stress (float): The maximum stress value among all loads.
        limit (float | None): An optional limit value for stress or percentage.
        loads (bool): Whether to exclude load details in the row.
        color (bool): Whether to exclude color formatting.

    Returns:
        tuple[Text]: The prepared row as a tuple of Text objects.
    """
    row = [
        Text(f"{i:02}", style="bold"),
        Text(f"{load.user_load.name}", style="bold") if load.user_load.name is not None else None,
    ]

    if show_loads:
        row.extend(
            [
                Text(f"{load.p :.1f}", style="black"),
                Text(f"{load.vx:.1f}", style="black"),
                Text(f"{load.vy:.1f}", style="black"),
                Text(f"{load.mx:.1f}", style="black"),
                Text(f"{load.my:.1f}", style="black"),
            ]
        )

    extra_data = format_rows(stress, percentaje, method, max_stress, limit, color)  # type: ignore
    row.extend(extra_data)

    return row


def display_page(start_idx: int, end_idx: int, all_rows: list[tuple[Any, ...]], table) -> None:
    """Display a page of rows in the output table.

    This function takes a range of indices and adds the corresponding rows to the table.
    The table with these rows is then displayed on the console.

    Args:
        start_idx (int): The starting index for the range of rows to be displayed.
        end_idx (int): The ending index for the range of rows to be displayed.
        all_rows (list[tuple[Any, ...]]): The list containing all the rows.
        table: The table object where the rows will be added.

    Returns:
        None: The function outputs the table to the console and returns None.
    """
    for row in all_rows[start_idx:end_idx]:
        table.add_row(*row)
    console.print(table)


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
        "ex",
        "ey",
        "Column",
        "Area(m²)",
        "Vol.(m³)",
        "Weight (t)",
    )
