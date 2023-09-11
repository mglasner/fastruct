"""Functions to handle table pagination."""
from collections.abc import Callable
from typing import Any

from rich.console import Console
from rich.table import Table

console = Console()


def display_page(start_idx: int, end_idx: int, all_rows: list[tuple[Any, ...]], table: Table) -> None:
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


def paginate_table(table: Table, rows: list[Any], rows_per_page: int, func: Callable[..., Any], *args: Any) -> None:
    """Paginate table."""
    num_pages = len(rows) // rows_per_page + (1 if len(rows) % rows_per_page else 0)
    for page in range(num_pages):
        start_idx = page * rows_per_page
        end_idx = start_idx + rows_per_page
        table, rows = func(*args)
        display_page(start_idx, end_idx, rows, table)
        if page < num_pages - 1:
            user_input = input(f"\nPage {page+1}/{num_pages}, press Enter to watch next results, 'q' to quit... ")
            if user_input == "q":
                break
