"""Configuración de la base de datos."""
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastruct.models.db import BaseModel

_session_local = None


def config_database():
    """Configuración de base de datos."""
    global _session_local  # noqa: PLW0603
    current_file_path = Path(__file__).resolve()
    installation_directory = current_file_path.parent
    database_url = f"sqlite:///{installation_directory / 'fastructdb.db'}"
    engine = create_engine(database_url)
    _session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    BaseModel.metadata.create_all(bind=engine)


def get_session_local() -> sessionmaker:
    """Obtener la sesión de la base de datos."""
    if _session_local is None:
        raise ValueError("_session_local es None")
    return _session_local


@contextmanager
def session_scope():
    """Proporciona una sesión transaccional en torno a una serie de operaciones."""
    session = get_session_local()()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
