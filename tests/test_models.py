import pytest
from sqlalchemy import create_engine, select, text
from sqlalchemy.engine import Engine, Connection, Transaction
from sqlalchemy.orm import Session

from models import Language

# pylint: disable=redefined-outer-name

@pytest.fixture(scope='module')
def engine():
    engine : Engine = create_engine('postgresql://postgres:postgres@localhost/dvdrental', future=True)
    yield engine

@pytest.fixture(scope='module')
def connection(engine):
    con : Connection = engine.connect()
    yield con
    con.close()

@pytest.fixture(scope='function')
def session(engine: Engine, connection: Connection):
    transaction : Transaction = connection.begin()
    session = Session(engine)
    yield session
    session.close()
    transaction.rollback()

def test_language_model(session : Session):
    stmt = select(Language)
    print(stmt)
    # result = connection.execute(stmt)
    # for row in result:
    #     print(row.language_id)
