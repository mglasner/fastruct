"""Get Foundation table."""
from rich.table import Table

from fastruct.models.foundation import Foundation


def get_table(foundations: list[Foundation]) -> Table:
    """Set table for get foundations command."""
    table = table_header()
    add_rows(table, foundations)
    return table


def add_rows(table: Table, foundations: list[Foundation]) -> None:
    """Add foundation data to table."""
    for foundation in foundations:
        table.add_row(
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
        )


def table_header() -> Table:
    """Set table headers and return table instance."""
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
