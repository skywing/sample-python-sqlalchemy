
from typing import List
from operator import attrgetter
from sqlalchemy import create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from models import Film, Language
import pytest

# pylint: disable=redefined-outer-name

@pytest.fixture(scope='class')
def engine():
    engine : Engine = create_engine('postgresql://postgres:postgres@localhost/dvdrental', future=True)
    yield engine

@pytest.fixture(scope='function')
def session(engine: Engine):
    Session = sessionmaker(bind=engine, future=True)
    session = Session()
    yield session
    session.rollback()

def test_language_model(session : Session):
    stmt = select(Language)
    languages : List[Language ]= session.execute(stmt).scalars().all()
    assert len(languages) == 6
    languages.sort(key=attrgetter('language_id'))
    assert languages[0].language_id == 1
    assert languages[0].name.strip() == 'English'

def test_film_model(session: Session):
    stmt = select(Film).where(Film.film_id == 1)
    film = session.execute(stmt).scalar_one_or_none()
    assert film.title == 'Academy Dinosaur'
    assert film.language.name.strip() == 'English'
