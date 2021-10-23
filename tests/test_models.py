
from typing import Any, List
from operator import attrgetter
from sqlalchemy import create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from models import Category, Film, Language, Actor, film_actor
import pytest

# pylint: disable=redefined-outer-name

@pytest.fixture(scope='class')
def engine():
    engine : Engine = create_engine('postgresql://postgres:postgres@localhost/dvdrental', future=True, echo=True)
    yield engine

@pytest.fixture(scope='function')
def session(engine: Engine):
    session_maker = sessionmaker(bind=engine, future=True)
    session = session_maker()
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
    film : Any = session.execute(stmt).scalar_one_or_none()
    assert film.title == 'Academy Dinosaur'
    assert film.language.name.strip() == 'English'
    assert len(film.categories) >= 1

def test_film_category_model(session: Session):
    stmt = select(Category).where(Category.name == 'Sports')
    category : Any = session.execute(stmt).scalar_one_or_none()
    assert category is not None
    assert category.category_id == 15
    assert len(category.films) == 74

def test_film_actor_association_model(session: Session):
    stmt = select(Film.title, Actor.first_name, Actor.last_name).join(Film.actors).where(Actor.actor_id == 107)
    films : Any = session.execute(stmt).all()
    assert len(films) == 42
    film = list(filter(lambda f: f.title == 'Chamber Italian', films))
    print(film)

