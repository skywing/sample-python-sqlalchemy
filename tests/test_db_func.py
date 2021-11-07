from datetime import datetime
from decimal import Decimal
from typing import Any
from sqlalchemy import create_engine, select, func
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import ProgrammingError
import pytest

# pylint: disable=redefined-outer-name, pointless-string statement

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

def test_func_group_concat(session: Session):
    stmt = select(
        func._group_concat("first name", "last name").label('concat_value')
    )
    result : Any = session.execute(stmt).one_or_none()
    assert result.concat_value == 'first name, last name'

def test_func_film_in_stock(session: Session):
    stmt = select(
        func.film_in_stock(1,1)
    )
    stocks: Any = session.execute(stmt).all()
    assert len(stocks) == 4
    assert stocks[0][0] == 1
    assert stocks[1][0] == 2
    assert stocks[2][0] == 3
    assert stocks[3][0] == 4

def test_func_film_not_in_stock(session: Session):
    with pytest.raises(ProgrammingError):
        stmt = select(
            func.get_customer_balance(524, datetime(2005, 7, 29))
        )
        balance = session.execute(stmt).scalar_one()
        assert balance == Decimal(45.88)

def test_func_inventory_held_by_customer(session: Session):
    stmt = select(
        func.inventory_held_by_customer(6)
    )
    inventory_id = session.execute(stmt).scalar_one_or_none()
    assert inventory_id is not None
    assert inventory_id == 554

def test_func_inventory_in_stock(session: Session):
    stmt = select(
        func.inventory_in_stock(6)
    )
    in_stock = session.execute(stmt).scalar_one()
    assert in_stock == False

    stmt = select(
        func.inventory_in_stock(20)
    )
    in_stock = session.execute(stmt).scalar_one()
    assert in_stock == True

def test_func_last_day(session: Session):
    stmt = select(
        func.last_day('2020-02-01')
    )
    last_day = session.execute(stmt).scalar_one()
    assert last_day == datetime(2020, 2, 29).date()

    stmt = select(
        func.last_day('2020-08-01')
    )
    last_day = session.execute(stmt).scalar_one()
    assert last_day == datetime(2020, 8, 31).date()
