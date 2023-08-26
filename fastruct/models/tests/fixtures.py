"""Pytest fixtures for model tests."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ..db import BaseModel
from ..foundation import Fundacion


@pytest.fixture(scope="session")
def engine():
    """Engine fixture."""
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="function")
def session(engine, request):
    """Session fixture."""
    connection = engine.connect()
    session = Session(bind=connection)

    def teardown():
        connection.close()
        session.close()

    request.addfinalizer(teardown)

    BaseModel.metadata.create_all(bind=engine)
    return session


@pytest.fixture
def fundacion_1_1_1(session: Session) -> Fundacion:
    """Fixture que crea una instancia de la clase Fundacion.

    Returns:
        Fundacion: Una instancia de la clase Fundacion.
    """
    fundacion = Fundacion(lx=1, ly=1, lz=1)
    session.add(fundacion)
    session.commit()

    return fundacion
