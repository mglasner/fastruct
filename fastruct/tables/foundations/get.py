"""Get Foundation table."""
from typing import Any

from rich.table import Table
from rich.text import Text

from fastruct.models.foundation import Foundation


def get_table(foundations: list[Foundation]) -> tuple[Table, list[Any]]:
    """Set table for get foundations command."""
    table = table_header()
    rows = generate_rows(table, foundations)
    return table, rows


def generate_rows(table: Table, foundations: list[Foundation]) -> list[Any]:
    """Add foundation data to table."""
    return [
        [
            str(foundation.id),
            foundation.name,
            foundation.description,
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
        ]
        for foundation in foundations
    ]


def table_header() -> Table:
    """Set table headers and return table instance."""
    table = Table(
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

    table.title = Text("Foundations", style="black on white bold")
    table.show_lines = True
    return table
