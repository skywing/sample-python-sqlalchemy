from sqlalchemy import MetaData
from sqlalchemy import Table, Column
from sqlalchemy import Integer, String, DateTime
from sqlalchemy import select, func, and_, or_
from sqlalchemy.sql.elements import BooleanClauseList
from sqlalchemy.sql.schema import Identity

metadata = MetaData(schema='unittest')

test_actor_table = Table(
    "test_actor",
    metadata,
    Column('actor_id', Integer, Identity(start=1, cycle=True), primary_key=True),
    Column('first_name', String(45), nullable=False),
    Column('last_name', String(45), nullable=False),
    Column('last_update', DateTime, server_default=func.now())
)

def test_validate_actor_table():
    assert test_actor_table.c.actor_id.name == 'actor_id'
    assert test_actor_table.primary_key is not None

    stmt = select(test_actor_table)
    assert str(stmt) == 'SELECT test_actor.actor_id, test_actor.first_name, test_actor.last_name, test_actor.last_update \nFROM test_actor'

def test_metadata_table():
    actor_tbl = metadata.tables['unittest.test_actor']
    assert actor_tbl.name == 'test_actor'
    assert len(actor_tbl.columns) == 4
    assert actor_tbl.schema == 'unittest'

def test_compile_sql():
    compiled = (test_actor_table.c.first_name == 'Nick').compile()
    assert compiled.string.endswith(':first_name_1')is True
    params = compiled.params
    print(params)
    assert params is not None
    assert len(params) == 1
    assert 'first_name_1' in params == {'first_name_1': 'Nick'}

def test_sql_and():
    stmt = (and_(
        test_actor_table.c.actor_id.between(1,10),
        test_actor_table.c.last_name != 'Chase'
    ))
    assert isinstance(stmt, BooleanClauseList)
    stmt_str = stmt.__str__()
    assert stmt_str.index('BETWEEN') > -1
    assert stmt_str.index('AND') > -1

def test_sql_or():
    stmt = (or_(
        test_actor_table.c.first_name != None,
        test_actor_table.c.last_update == None
    ))
    assert isinstance(stmt, BooleanClauseList)
    stmt_str = stmt.__str__()
    assert stmt_str.index('OR') > -1
    assert stmt_str.index('IS NULL') > -1

