from datetime import datetime
from decimal import Decimal
from typing import Any, List
from operator import attrgetter
import pytest
from sqlalchemy import create_engine, select, func
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from models import Category, Film, Language, Actor, Store, Staff
from models import Rental, Payment

# pylint: disable=redefined-outer-name, pointless-string-statement

@pytest.fixture(scope='class')
def engine():
    engine : Engine = create_engine('postgresql://postgres:postgres@localhost:5438/dvdrental', future=True, echo=True)
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
    stmt = select(Film.film_id, Film.title, Actor.first_name, Actor.last_name).join(Film.actors).where(Actor.actor_id == 107)
    films : Any = session.execute(stmt).all()
    assert len(films) == 42
    film : Any = list(filter(lambda f: f.title == 'Chamber Italian', films))
    assert len(film) == 1
    assert film[0].film_id == 133

def test_film_inventory_store_model(session: Session):
    stmt = select(Film.film_id, Film.title, func.count(), Store.store_id)\
            .join(Film.stores)\
            .group_by(Film.film_id, Store.store_id)\
            .where(Store.store_id == 1)
    films_at_store : Any = session.execute(stmt).all()
    assert len(films_at_store) == 759
    film_inventory = list(filter(lambda fc: fc.film_id == 253, films_at_store))
    assert len(film_inventory) == 1
    assert film_inventory[0].count == 4

def test_staff_store_address_model(session: Session):
    stmt = select(Staff).where(Staff.staff_id == 2)
    staff = session.execute(stmt).scalar_one_or_none()
    assert staff is not None
    assert len(staff.stores) == 1
    staff_store : Store = staff.stores[0]
    assert staff_store.store_id == 2
    assert staff_store.address_id == 2
    assert staff_store.manager is not None
    assert staff_store.manager.first_name == 'Jon'
    assert staff_store.manager.email == 'Jon.Stephens@sakilastaff.com'
    
    assert staff.address.address_id == 4
    assert staff.address.city.city == 'Woodridge'


def test_store_address_model(session: Session):
    stmt = select(Store).where(Store.store_id == 1)
    store = session.execute(stmt).scalar_one_or_none()
    assert store is not None
    assert store.address is not None
    assert store.address.address == '47 MySakila Drive'
    '''
        The city is lazy load by default so accessing the city
        will trigger the session to execute query to load the city
        by the given city_id
    '''
    assert store.address.city.city == 'Lethbridge'
    '''
        The country is configured to use eager loading. When the above city is accessed
        and the country is loaded as part of the city loading with inner join.
        Example: country = relationship('Country', lazy='joined', innerjoin=True, uselist=False)
    '''
    assert store.address.city.country.country == 'Canada'

def test_rental_customer_model(session: Session):
    stmt = select(Rental).where(Rental.rental_id == 2)
    rental = session.execute(stmt).scalar_one_or_none()
    assert rental is not None
    assert rental.rental_date >= datetime(2005, 5, 24)
    assert rental.staff.email == 'Mike.Hillyer@sakilastaff.com'
    assert rental.customer.email == 'tommy.collazo@sakilacustomer.org'
    assert rental.film.title == 'Freaky Pocus'

def test_payment_rental_customer_staff(session: Session):
    stmt = select(Payment).where(Payment.payment_id == 17503)
    payment = session.execute(stmt).scalar_one_or_none()
    assert payment is not None
    assert payment.amount == pytest.approx(Decimal(7.99))
    assert payment.payment_date.date() >= datetime(2007, 2, 15).date()
    assert payment.customer.email == 'peter.menard@sakilacustomer.org'
    assert payment.staff.email == 'Jon.Stephens@sakilastaff.com'
