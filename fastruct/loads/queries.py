"""Loads queries and database related functions."""
from models.user_load import UserLoad
from sqlalchemy.orm import Session


def is_load_duplicated(session: Session, load: dict) -> bool:
    """Cjeck if load exist in database.

    Args:
        session (Session): Database session..
        load (dict): Load values to be verified.

    Returns:
        bool: True is load exist, false otherwise.
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
