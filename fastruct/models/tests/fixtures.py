"""Pytest fixtures for model tests."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ..db import BaseModel
from ..foundation import Foundation
from ..project import Project


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
def project1(session: Session) -> Project:
    """Project instance.

    Returns:
        Project: An instance of Project.
    """
    project = Project(name="my project", code="12345", description="my description")
    session.add(project)
    session.commit()

    return project


@pytest.fixture
def foundation1(session: Session, project1: Project) -> Foundation:
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
        project_id=project1.id,
    )
    session.add(foundation)
    session.commit()

    return foundation
