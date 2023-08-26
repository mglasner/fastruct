"""Funciones auxiliares para el módulo commands."""
from models.user_load import UserLoad
from rich.table import Table
from sqlalchemy.orm import Session


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


def is_load_duplicated(session: Session, load: dict) -> bool:
    """Verificar si ya existe una carga con los valores especificados en la base de datos.

    Args:
        session (Session): Sesión de la base de datos en uso.
        esfuerzos (dict): Diccionario con los valores de la carga que se quiere verificar.

    Returns:
        bool: Verdadero si la carga ya existe, falso en caso contrario.
    """
    existing_load = (
        session.query(UserLoad)
        .filter_by(
            foundation_id=load["foundation_id"],
            p=load["p"],
            vx=load["vx"],
            vy=load["vy"],
            mx=load["mx"],
            my=load["my"],
            ex=load["ex"],
            ey=load["ey"],
        )
        .first()
    )
    return existing_load is not None
