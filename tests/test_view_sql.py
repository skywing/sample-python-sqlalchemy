import pytest
from decimal import Decimal
from typing import Any
from sqlalchemy import create_engine, select, func
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql.expression import desc, text
from models import Category, Film, Actor, Store, Staff
from models import Rental, Payment, Customer, Address, City, Country
from models import film_actor, film_category, inventory

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

def test_view_customer_list(session: Session):
    '''
    CREATE VIEW public.customer_list AS
    SELECT cu.customer_id AS id,
        (((cu.first_name)::text || ' '::text) || (cu.last_name)::text) AS name,
        a.address,
        a.postal_code AS "zip code",
        a.phone,
        city.city,
        country.country,
            CASE
                WHEN cu.activebool THEN 'active'::text
                ELSE ''::text
            END AS notes,
        cu.store_id AS sid
    FROM (((public.customer cu
        JOIN public.address a ON ((cu.address_id = a.address_id)))
        JOIN public.city ON ((a.city_id = city.city_id)))
        JOIN public.country ON ((city.country_id = country.country_id)));
    '''
    stmt = select(
            Customer.customer_id.label('id'),
            func.concat(Customer.first_name, ' ', Customer.last_name).label('name'),
            Address.address,
            Address.postal_code.label('zip_code'),
            Address.phone,
            City.city,
            Country.country
            )\
            .select_from(Customer)\
            .join(Address)\
            .join(City)\
            .join(Country)
    customers = session.execute(stmt).all()

    assert len(customers) == 599
    filter_results = list(filter(lambda c: c.id == 14, customers))
    assert len(filter_results) == 1
    customer = filter_results[0]
    assert customer is not None
    assert customer.name == 'Betty White'
    assert customer.address == '770 Bydgoszcz Avenue'
    assert customer.zip_code == '16266'

def test_view_film_list_with_db_func(session: Session):
    '''
    SELECT film.film_id AS fid,
    film.title,
    film.description,
    category.name AS category,
    film.rental_rate AS price,
    film.length,
    film.rating,
    public.group_concat((((actor.first_name)::text || ' '::text) || (actor.last_name)::text)) AS actors
    FROM ((((public.category
        LEFT JOIN public.film_category ON ((category.category_id = film_category.category_id)))
        LEFT JOIN public.film ON ((film_category.film_id = film.film_id)))
        JOIN public.film_actor ON ((film.film_id = film_actor.film_id)))
        JOIN public.actor ON ((film_actor.actor_id = actor.actor_id)))
    GROUP BY film.film_id, film.title, film.description, category.name, film.rental_rate, film.length, film.rating;
    '''
    stmt = select(
        Film.film_id.label('fid'),
        Film.description,
        Category.name.label('description'),
        Film.rental_rate.label('price'),
        Film.length,
        Film.rating,
        func.public.group_concat(func.concat(Actor.first_name , ' ', Actor.last_name)).label('actors')
    ).select_from(Category)\
    .join(film_category)\
    .join(Film)\
    .join(film_actor)\
    .join(Actor)\
    .group_by(Film.film_id, Film.title, Film.description, Category.name, Film.rental_rate, Film.length, Film.rating)\
    .order_by(Film.film_id)

    films = session.execute(stmt).all()
    assert len(films) == 997
    film : Any = films[0]
    assert film.fid == 1
    assert film.actors == 'Rock Dukakis, Mary Keitel, Johnny Cage, Penelope Guiness, Sandra Peck, Christian Gable, Oprah Kilmer, Warren Nolte, Lucille Tracy, Mena Temple'
    assert film.price == Decimal('0.99')

def test_view_nice_but_slower_film_list_with_nested_db_function(session: Session):
    '''
    SELECT film.film_id AS fid,
    film.title,
    film.description,
    category.name AS category,
    film.rental_rate AS price,
    film.length,
    film.rating,
    public.group_concat((((upper("substring"((actor.first_name)::text, 1, 1)) || lower("substring"((actor.first_name)::text, 2))) || upper("substring"((actor.last_name)::text, 1, 1))) || lower("substring"((actor.last_name)::text, 2)))) AS actors
    FROM ((((public.category
        LEFT JOIN public.film_category ON ((category.category_id = film_category.category_id)))
        LEFT JOIN public.film ON ((film_category.film_id = film.film_id)))
        JOIN public.film_actor ON ((film.film_id = film_actor.film_id)))
        JOIN public.actor ON ((film_actor.actor_id = actor.actor_id)))
    GROUP BY film.film_id, film.title, film.description, category.name, film.rental_rate, film.length, film.rating;
    '''
    stmt = select(
        Film.film_id, 
        Film.description,
        Category.name.label('description'),
        Film.rental_rate.label('price'),
        Film.length,
        Film.rating,
        func.public.group_concat(func.concat(
                                    func.upper(func.substring(Actor.first_name,1,1)),
                                    func.lower(func.substring(Actor.first_name,2)),
                                    func.upper(func.substring(Actor.last_name,1,1)),
                                    func.lower(func.substring(Actor.last_name,2))
        )).label('actors')
    ).select_from(Category)\
    .join(film_category)\
    .join(Film)\
    .join(film_actor)\
    .join(Actor)\
    .group_by(Film.film_id, Film.title, Film.description, Category.name, Film.rental_rate, Film.length, Film.rating)\
    .order_by(Film.film_id)

    films = session.execute(stmt).all()
    assert len(films) == 997
    film : Any = films[0]
    assert film.film_id == 1
    assert film.actors == 'RockDukakis, MaryKeitel, JohnnyCage, PenelopeGuiness, SandraPeck, ChristianGable, OprahKilmer, WarrenNolte, LucilleTracy, MenaTemple'
    assert film.price == Decimal('0.99')

def test_view_sales_by_film_category(session: Session):
    '''
    SELECT c.name AS category,
    sum(p.amount) AS total_sales
    FROM (((((public.payment p
        JOIN public.rental r ON ((p.rental_id = r.rental_id)))
        JOIN public.inventory i ON ((r.inventory_id = i.inventory_id)))
        JOIN public.film f ON ((i.film_id = f.film_id)))
        JOIN public.film_category fc ON ((f.film_id = fc.film_id)))
        JOIN public.category c ON ((fc.category_id = c.category_id)))
    GROUP BY c.name
    ORDER BY (sum(p.amount)) DESC;
    '''
    stmt = select(
        Category.name.label('category'),
        func.sum(Payment.amount).label('total_sales')
    ).select_from(Payment)\
    .join(Rental)\
    .join(inventory)\
    .join(Film)\
    .join(film_category)\
    .join(Category)\
    .group_by(Category.name)\
    .order_by(desc(func.sum(Payment.amount)))

    sales = session.execute(stmt).all()
    assert len(sales) == 16
    first : Any = sales[0]
    assert first.category == 'Sports'
    assert first.total_sales == Decimal(str(4892.19))
    assert first.total_sales == round(Decimal(4892.19),2)

def test_view_sales_by_store(session: Session):
    '''
    SELECT (((c.city)::text || ','::text) || (cy.country)::text) AS store,
    (((m.first_name)::text || ' '::text) || (m.last_name)::text) AS manager,
    sum(p.amount) AS total_sales
    FROM (((((((public.payment p
        JOIN public.rental r ON ((p.rental_id = r.rental_id)))
        JOIN public.inventory i ON ((r.inventory_id = i.inventory_id)))
        JOIN public.store s ON ((i.store_id = s.store_id)))
        JOIN public.address a ON ((s.address_id = a.address_id)))
        JOIN public.city c ON ((a.city_id = c.city_id)))
        JOIN public.country cy ON ((c.country_id = cy.country_id)))
        JOIN public.staff m ON ((s.manager_staff_id = m.staff_id)))
    GROUP BY cy.country, c.city, s.store_id, m.first_name, m.last_name
    ORDER BY cy.country, c.city;
    '''
    stmt = select(
        # Payment, Store, Address, City, Country, Staff
        func.concat(City.city, ',', Country.country).label('store'),
        func.concat(Staff.first_name, ' ', Staff.last_name).label('manager'),
        func.sum(Payment.amount).label('total_sales')
    ).select_from(Payment)\
    .join(Rental)\
    .join(inventory)\
    .join(Store)\
    .join(Address)\
    .join(City)\
    .join(Country)\
    .join(Staff, onclause=text('Staff.staff_id = Store.manager_staff_id'))\
    .group_by(Country.country, City.city, Store.store_id, Staff.first_name, Staff.last_name)\
    .order_by(Country.country, City.city)

    sales_by_store = session.execute(stmt).all()
    assert len(sales_by_store) == 2
    store_sales = sales_by_store[0]
    assert store_sales.store == 'Woodridge,Australia'
    assert store_sales.manager == 'Jon Stephens'
    assert store_sales.total_sales == round(Decimal(30683.13), 2)


def test_view_staff_list(session: Session):
    '''
    SELECT s.staff_id AS id,
    (((s.first_name)::text || ' '::text) || (s.last_name)::text) AS name,
    a.address,
    a.postal_code AS "zip code",
    a.phone,
    city.city,
    country.country,
    s.store_id AS sid
    FROM (((public.staff s
        JOIN public.address a ON ((s.address_id = a.address_id)))
        JOIN public.city ON ((a.city_id = city.city_id)))
        JOIN public.country ON ((city.country_id = country.country_id)));
    '''
    stmt = select(
        Staff.staff_id.label('id'),
        func.concat(Staff.first_name, ' ', Staff.last_name).label('name'),
        Address.address,
        Address.postal_code.label('zip_code'),
        Address.phone,
        City.city,
        Country.country,
        Staff.store_id.label('sid')
    ).select_from(Staff)\
    .join(Address)\
    .join(City)\
    .join(Country)\
    .order_by(Staff.staff_id)

    staffs = session.execute(stmt).all()
    assert len(staffs) == 2
    staff : Any = staffs[0]
    assert staff.id == 1
    assert staff.name == 'Mike Hillyer'
    assert staff.address == '23 Workhaven Lane'
    assert staff.zip_code == ''
    assert staff.phone == '14033335568'
    assert staff.city == 'Lethbridge'
    assert staff.country == 'Canada'
    assert staff.sid == 1
