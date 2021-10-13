'''
    The SQLAlchemy connection is not autocommit by default unless
    it is setup when creating the connection. Without explicit
    commit, the insert, update, delete statemennt will be rollback.
'''
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
import pytest

# pylint: disable=redefined-outer-name

@pytest.fixture(scope='class')
def engine() -> Engine:
    '''Setup the engine for test cases in the module'''
    return create_engine('postgresql://postgres:postgres@localhost/dvdrental', future=True)

@pytest.fixture(scope='class', autouse=True)
def create_test_language_table(engine: Engine):
    with engine.connect() as conn:
        with conn.begin() as tx:
            conn.execute(text('drop table if exists test_language'))
            conn.execute(text('create table test_language(language_id integer, name character(20) NOT NULL, last_update timestamp without time zone DEFAULT now() NOT NULL)'))
            conn.execute(text('insert into test_language(language_id, name) select language_id, name from language'))
            tx.commit()

class TestConnection:
    def test_execute(self, engine: Engine):
        with engine.connect() as conn:
            results = conn.execute(text('select * from language order by language_id')).all()
            assert len(results) >= 6

            assert results[0].language_id == 1
            assert results[0].name.strip() == 'English'
            assert results[0].last_update == datetime.strptime('2006-02-15 10:02:19', '%Y-%m-%d %H:%M:%S')

    def test_complex_query(self, engine: Engine):
        with engine.connect() as conn:
            results = conn.execute(text('''
                select f.film_id, f.title, c.name as category_name, l.name as language_name
                from film f inner join film_category fc on f.film_id = fc.film_id
                inner join category c on fc.category_id = c.category_id
                inner join language l on f.language_id = l.language_id
            ''')).all()

            assert len(results) == 1000

    def test_insert(self, engine: Engine):
        with engine.connect() as conn:
            result = conn.execute(
                        text('insert into test_language(language_id, name, last_update) values(:id, :name, :last_update)'),
                        [{'id': 100, 'name': 'pytest_test', 'last_update': datetime.now()}])
            assert result.rowcount == 1

            rows = conn.execute(
                text('select language_id, name, last_update from test_language where name = :name'),
                [{'name': 'pytest_test'}]
            )
            assert rows.rowcount == 1

            data = rows.one_or_none()
            assert data is not None
            assert data.language_id > 0
            assert data.name.strip() == 'pytest_test'
            assert data.last_update <= datetime.now()

            # no explicit commit so the above sql transaction will rollback
            # call to conn.close() is not needed as context manager is used to manage the 
            # connection. This is written explicit to demonstrate that the connection close 
            # is called without explicit calling commit or using autocommit.
            conn.close()

    def test_update(self, engine: Engine):
        with engine.connect() as conn:
            result = conn.execute(
                        text('update test_language set name = :new_name, last_update = :last_update where language_id = :id'),
                        [{'new_name': 'Not German', 'last_update': datetime.now(), 'id': 6}])
            assert result.rowcount == 1

            language = conn.execute(
                text('select name from test_language where language_id = :language_id'),
                [{'language_id': 6}]
            ).one_or_none()

            assert language.name.strip() == 'Not German'


    def test_delete(self, engine: Engine):
        with engine.connect() as conn:
            result = conn.execute(
                        text('delete from test_language where language_id = :language_id'), [{'language_id': 4}])
            assert result.rowcount == 1
            language = conn.execute(
                text('select name from test_language where language_id = :language_id'),
                [{'language_id': 4}]
            ).one_or_none()
            assert language is None
        
    def test_autocommit(self, engine: Engine):
        with engine.connect().execution_options(isolation_level='AUTOCOMMIT') as conn:
            result = conn.execute(
                    text('insert into test_language(language_id, name, last_update) values(:id, :name, :last_update)'),
                    [{'id': 1001, 'name': 'pytest_test', 'last_update': datetime.now()}])
            assert result.rowcount == 1

        # Use another connection to query the data that is not in the same transaction
        with engine.connect() as conn2:
            language = conn2.execute(
                text('select language_id, name, last_update from test_language where language_id = :language_id'),
                [{'language_id': 1001}]
            ).one_or_none()
            assert language is not None
            assert language.language_id == 1001
            assert language.name.strip() == 'pytest_test'
            assert language.last_update <= datetime.now()
