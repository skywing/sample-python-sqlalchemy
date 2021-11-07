from sqlalchemy import create_engine, text, MetaData
from sqlalchemy import Table, Column
from sqlalchemy import Integer, String, DateTime
from sqlalchemy import select, func, and_, or_
from sqlalchemy.engine import Engine
import pytest

# pylint: disable=redefined-outer-name

@pytest.fixture(scope='class')
def engine() -> Engine:
    return create_engine('postgresql://postgres:postgres@localhost:5438/dvdrental', future=True)

@pytest.fixture(scope='class')
def create_test_actor_table(engine: Engine):
    with engine.connect() as conn:
        with conn.begin() as tx:
            conn.execute(text('drop table if exists test_actor'))
            conn.execute(text('create table test_actor( \
                actor_id SERIAL PRIMARY KEY, \
                first_name character varying(45), \
                last_name character varying(45), \
                last_update timestamp without time zone DEFAULT now() NOT NULL)'))
            conn.execute(text('insert into test_actor (first_name, last_name) \
                select first_name, last_name from actor \
            '))

@pytest.fixture(scope='class')
def test_actor_table(engine: Engine, create_test_actor_table):
    with engine.connect() as conn:
        metadata = MetaData()
        metadata.reflect(conn)
        return metadata.tables['test_actor']

def test_actor_insert(engine: Engine, test_actor_table: Table):
    with engine.connect() as conn:
        result = conn.execute(
            test_actor_table.insert(), [
                {'first_name': 'John', 'last_name': 'Wick'},
                {'first_name': 'Sofia', 'last_name': 'H'}
            ]
        )
        assert result.rowcount == 2

def test_actor_select(engine: Engine, test_actor_table: Table):
    with engine.connect() as conn:
        stmt = (select(test_actor_table.c.first_name, test_actor_table.c.last_name)\
            .where(test_actor_table.c.actor_id == 161))
        data = conn.execute(stmt).one_or_none()
        assert data.first_name == 'Harvey'
        assert data.last_name == 'Hope'
