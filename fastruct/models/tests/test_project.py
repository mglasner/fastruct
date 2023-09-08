"""Project model tests."""
from sqlalchemy.orm import Session

from ..project import Project
from .fixtures import engine, project1, session


def test_create_project(session: Session, project1: Project):
    """Create an instance in database."""
    projects = session.query(Project).all()
    project = projects[0]
    assert len(projects) == 1
    assert project.name == "my project"
    assert project.description == "my description"
    assert project.code == "12345"
    assert project.is_active is False
