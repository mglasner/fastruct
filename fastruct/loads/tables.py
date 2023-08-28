"""Loads Rich tables configuration module."""
from rich.table import Table


def tabla_cargas(fundacion) -> Table:
    """Crear una tabla para visualizar las cargas aplicadas sobre una fundación."""
    table = Table(
        "#",
        "P",
        "Vx",
        "Vy",
        "Mx",
        "My",
        "⅓ central x",
        "⅓ central y",
        "🔺 x",
        "🔺 y",
        "σx max",
        "σx min",
        "σy max",
        "σy min",
    )
    table.title = str(fundacion)
    return table
