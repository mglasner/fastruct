"""Projects Rich tables configuration module."""
from rich.table import Table


def projects_table() -> Table:
    """Projects table configuration."""
    table = Table(
        "#",
        "ID",
        "Name",
        "Code",
        "Description",
    )
    table.title = "Projects"
    return table
