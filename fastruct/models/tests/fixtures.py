"""Pytest fixtures for model tests."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ..db import BaseModel
from ..foundation import Foundation


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
def foundation_1_1_1(session: Session) -> Foundation:
    """Foundation instance.

    Returns:
        Foundation: An instance of Foundation.
    """
    foundation = Foundation(
        lx=1,
        ly=1,
        lz=1,
        depth=1,
        ex=0.1,
        ey=0.1,
        col_x=0.15,
        col_y=0.15,
        name="my foundation",
        description="my description",
    )
    session.add(foundation)
    session.commit()

    return foundation
