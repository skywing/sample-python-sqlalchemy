from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, \
        TIMESTAMP, TEXT, DECIMAL, SMALLINT, func, text, Index, Sequence
from sqlalchemy.orm import relationship, backref, registry
from sqlalchemy.sql.schema import MetaData
from sqlalchemy.sql.sqltypes import ARRAY

mapper_registry = registry(metadata=MetaData(schema='public'))

def create_tsvector(*args):
    exp = args[0]
    for value in args[1:]:
        exp += ' ' + value
    return func.to_tsvector('english', exp)

def to_tsvector_ix(*columns):
    cols = " || ' ' || ".join(columns)
    return func.to_tsvector('english', text(cols))

@mapper_registry.mapped
class Actor():
    __tablename__ = 'actor'
    actor_id = Column('actor_id', Integer, Sequence('actor_actor_id_seq'), primary_key=True)
    first_name = Column('first_name', String(45), nullable=False)
    last_name = Column('last_name', String(45), nullable=False)
    last_update = Column('last_update', TIMESTAMP, nullable=False, default=datetime.utcnow)

@mapper_registry.mapped
class Language():
    __tablename__ = 'language'
    language_id = Column('language_id', Integer, Sequence('language_language_id_seq'), primary_key=True)
    name = Column('name', String(20), nullable=False)
    last_update = Column('last_update', TIMESTAMP, nullable=False, default=datetime.utcnow)

@mapper_registry.mapped
class Film():
    __tablename__ = 'film'
    film_id = Column('film_id', Integer, Sequence('film_film_id_seq'), primary_key=True)
    title = Column('title', String(255), nullable=False)
    description = Column('description', TEXT)
    release_year = Column('release_year', Integer)
    language_id = Column('language_id', Integer, ForeignKey('language.language_id'))
    rental_duration = Column('rental_duration', Integer, nullable=False, default=3)
    rental_rate = Column('rental_rate', DECIMAL(4, 2), nullable=False, default=4.9)
    length = Column('length', SMALLINT)
    replacement_cost = Column('replacement_cost', DECIMAL(5,2), nullable=False, default=19.99)
    rating = Column('rating', String(10), default='G')
    last_update = Column('last_update', TIMESTAMP, nullable=False, default=datetime.utcnow)
    special_features = Column('special_features', ARRAY(TEXT))
    fulltext = Column('fulltext', TEXT)

    __table_args__ = (
        Index('ix_film_fulltext', to_tsvector_ix('title', 'description'), postgresql_using='gin'),
    )

    language = relationship('Language')

@mapper_registry.mapped
class Category():
    __tablename__ = 'category'
    category_id = Column('category_id', Integer, Sequence('category_category_id_seq'), primary_key=True)
    name = Column('name', String(25), nullable=False)
    last_update = Column('last_update', TIMESTAMP, nullable=False, default=datetime.utcnow)

film_category = Table('film_category', )