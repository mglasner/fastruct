"""Get Foundation loads table."""
from rich.table import Table

from fastruct.models.foundation import Foundation


def get_loads_table(foundation: Foundation) -> Table:
    """Set table for get loads foundations command."""
    table = table_header(foundation)
    add_rows(table, foundation)
    return table


def add_rows(table: Table, foundation: Foundation) -> None:
    """Add foundation loads data to table."""
    for i, (user_load, load) in enumerate(zip(foundation.user_loads, foundation.seal_loads, strict=True), start=1):
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


def table_header(foundation: Foundation) -> Table:
    """Set table headers and return table instance."""
    table = Table("#", "ID", "NAME", "P", "Vx", "Vy", "Mx", "My")
    table.title = str(foundation)
    table.caption = "(value): loads at the f. CG and f. seal level"
    table.show_lines = True
    return table
