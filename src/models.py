from datetime import datetime
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy import TIMESTAMP, TEXT, DECIMAL, SMALLINT, Index, LargeBinary, BOOLEAN
from sqlalchemy import func, text, Sequence
from sqlalchemy.orm import relation, relationship, backref, registry
from sqlalchemy.sql.expression import null
from sqlalchemy.sql.schema import MetaData
from sqlalchemy.sql.sqltypes import ARRAY, Time
from sqlalchemy.sql.traversals import ColIdentityComparatorStrategy

mapper_registry = registry(metadata=MetaData(schema='public'))

def create_tsvector(*args):
    exp = args[0]
    for value in args[1:]:
        exp += ' ' + value
    return func.to_tsvector('english', exp)

def to_tsvector_ix(*columns):
    cols = " || ' ' || ".join(columns)
    return func.to_tsvector('english', text(cols))

film_category = Table(
    'film_category',
    mapper_registry.metadata,
    Column('film_id', Integer, ForeignKey('film.film_id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('category.category_id'), primary_key=True),
    Column('last_update', TIMESTAMP, nullable=False, default=datetime.utcnow)
)

film_actor = Table(
    'film_actor',
    mapper_registry.metadata,
    Column('actor_id', Integer, ForeignKey('actor.actor_id'), primary_key=True),
    Column('film_id', Integer, ForeignKey('film.film_id'), primary_key=True),
    Column('last_update', TIMESTAMP, nullable=False, default=datetime.utcnow)
)

inventory = Table(
    'inventory',
    mapper_registry.metadata,
    Column('inventory_id', Integer, Sequence('inventory_inventory_id_seq'), primary_key=True),
    Column('film_id', Integer, ForeignKey('film.film_id')),
    Column('store_id', Integer, ForeignKey('store.store_id')),
    Column('last_update', TIMESTAMP, nullable=False, default=datetime.utcnow)
)

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

    language = relationship('Language')
    categories = relationship('Category', secondary=film_category, backref='films')
    actors = relationship('Actor', secondary=film_actor, backref='actors')
    stores = relationship('Store', secondary=inventory, backref='stores')
    __table_args__ = (
        Index('ix_film_fulltext', to_tsvector_ix('title', 'description'), postgresql_using='gin'),
    )

@mapper_registry.mapped
class Category():
    __tablename__ = 'category'
    category_id = Column('category_id', Integer, Sequence('category_category_id_seq'), primary_key=True)
    name = Column('name', String(25), nullable=False)
    last_update = Column('last_update', TIMESTAMP, nullable=False, default=datetime.utcnow)

@mapper_registry.mapped
class Store():
    __tablename__ = 'store'
    store_id = Column('store_id', Integer, Sequence('store_store_id_seq'), primary_key=True)
    manager_staff_id = Column('manager_staff_id', ForeignKey('staff.staff_id'), nullable=False)
    address_id = Column('address_id', ForeignKey('address.address_id'), nullable=False)
    last_update = Column('last_update', TIMESTAMP, nullable=False, default=datetime.utcnow)
    '''
        The store can only be in one location, so set the relationship to return a single
        scalar object instead of list.
    '''
    address = relationship('Address', uselist=False)

@mapper_registry.mapped
class Staff():
    __tablename__ = 'staff'
    staff_id = Column('staff_id', Integer, Sequence('staff_staff_id_seq'), primary_key=True)
    first_name = Column('first_name', String(45), nullable=False)
    last_name = Column('last_name', String(45), nullable=False)
    address_id = Column('address_id', Integer, ForeignKey('address.address_id'), nullable=False)
    email = Column('email', String(50))
    store_id = Column('store_id', Integer, ForeignKey('store.store_id'), nullable=False)
    username = Column('username', String(16), nullable=False)
    password = Column('password', String(40))
    last_update = Column('last_update', TIMESTAMP, nullable=False, default=datetime.utcnow)
    picture = Column('picture', LargeBinary)

    '''
        This assume the staff can be a manager for multiple store.
        If it is a a staff can be only the manager for a store, we can set the uselist to False.
        Example: stores = relationship('Store', foreign_keys='Store.manager_staff_id', uselist=False)
    '''
    stores = relationship('Store', foreign_keys='Store.manager_staff_id', backref='manager')
    address = relationship('Address')

@mapper_registry.mapped
class Address():
    __tablename__ = 'address'
    address_id = Column('address_id', Integer, Sequence('address_address_id_seq'), primary_key=True)
    address = Column('address', String(50), nullable=False)
    address2 = Column('address2', String(50))
    district = Column('district', String(20), nullable=False)
    city_id = Column('city_id', ForeignKey('city.city_id'), nullable=False)
    postal_code = Column('postal_code', String(10))
    phone = Column('phone', String(20), nullable=False)
    last_update = Column('last_update', TIMESTAMP, nullable=False, default=datetime.utcnow)
    city = relationship('City')

@mapper_registry.mapped
class City():
    __tablename__ = 'city'
    city_id = Column('city_id', Integer, Sequence('city_city_id_seq'), primary_key=True)
    city = Column('city', String(50), nullable=False)
    country_id = Column('country_id', Integer, ForeignKey('country.country_id'), nullable=False)
    last_update = Column('last_update', TIMESTAMP, nullable=False, default=datetime.utcnow)
    '''
        Use eager loading so the country is loaded as part of the inner joined query
    '''
    country = relationship('Country', lazy='joined', innerjoin=True)


@mapper_registry.mapped
class Country():
    __tablename__ = 'country'
    country_id = Column('country_id', Integer, Sequence('country_country_id_seq'), primary_key=True)
    country = Column('country', String(50), nullable=False)
    last_update = Column('last_update', TIMESTAMP, nullable=False, default=datetime.utcnow)

@mapper_registry.mapped
class Rental():
    __tablename__ = 'rental'
    rental_id = Column('rental_id', Integer, Sequence('rental_rental_id_seq'), primary_key=True)
    rental_date = Column('rental_date', TIMESTAMP, nullable=False)
    inventory_id = Column('inventory_id', Integer, ForeignKey('inventory.inventory_id'), nullable=False)
    customer_id = Column('customer_id', Integer, ForeignKey('customer.customer_id'), nullable=False)
    return_date = Column('return_date', TIMESTAMP)
    staff_id = Column('staff_id', Integer, ForeignKey('staff.staff_id'), nullable=False)
    last_update = Column('last_update', TIMESTAMP, nullable=False, default=datetime.utcnow)

    film = relationship('Film', secondary=inventory, uselist=False)
    staff = relationship('Staff', lazy='joined', innerjoin=True)
    customer = relationship('Customer', lazy='joined', innerjoin=True)

@mapper_registry.mapped
class Customer():
    __tablename__ = 'customer'
    customer_id = Column('customer_id', Integer, Sequence('customer_customer_id_seq'), primary_key=True)
    store_id = Column('store_id', Integer, ForeignKey('store.store_id'), nullable=False)
    first_name = Column('first_name', String(45), nullable=False)
    last_name = Column('last_name', String(45), nullable=False)
    email = Column('email', String(50))
    address_id = Column('address_id', Integer, ForeignKey('address.address_id'), nullable=False)
    activebool = Column('activebool', BOOLEAN, default=True, nullable=False)
    create_date = Column('create_date', TIMESTAMP, nullable=False, default=datetime.utcnow)
    last_update = Column('last_update', TIMESTAMP, nullable=False, default=datetime.utcnow)
    active = Column('active', Integer)

    store = relationship('Store')
    address = relationship('Address')

@mapper_registry.mapped
class Payment():
    __tablename__ = 'payment'
    payment_id = Column('payment_id', Integer, Sequence('payment_payment_id_seq'), primary_key=True)
    customer_id = Column('customer_id', Integer, ForeignKey('customer.customer_id'), nullable=False)
    staff_id = Column('staff_id', Integer, ForeignKey('staff.staff_id'), nullable=False)
    rental_id = Column('rental_id', Integer, ForeignKey('rental.rental_id'), nullable=False)
    amount = Column('amount', DECIMAL(5,2), nullable=False)
    payment_date = Column('payment_date', TIMESTAMP, nullable=False)

    customer = relationship('Customer')
    staff = relationship('Staff')
    rental = relationship('Rental', backref='payment')
