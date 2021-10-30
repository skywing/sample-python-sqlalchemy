# Learning Python Data Access and ORM Toolkit with SQLAlchemy
This repository is a Python data access and ORM learning project using SQLAlchemy SQL Toolkit and Object Relational Mapper version 1.4+ / 2.0. The Postgres DVD rental database is selected as the sample database as it has all the common table relationship patterns used in many typical web and standalone applications.

This learning project focus on the SQLAlchemy foundational usage:
- Connection
- Session
- Object & data mapping
- Object relationships
    - one to one
    - one to many
    - many to many
- Use of built-in & user defined database functions


## Setup and Install Dependencies
### Python
```zsh
pip install -r requirements.txt
```

## Run All Unit Test Cases with Pytest
```zsh
pytest tests
```

## Postgres Database
Follow instruction in this [Load PostgreSQL Sample Database article](https://www.postgresqltutorial.com/load-postgresql-sample-database/) to setup sample database in Postgres if you are having problem use the Postgres database docker image in this repository.

## Sample Database - Postgres DVD Rental ER Model
[The DVD rental database](https://www.postgresqltutorial.com/postgresql-sample-database/) represents the business processes of a DVD rental store. The DVD rental database has many objects including:

- 15 tables
- 1 trigger
- 7 views
- 8 functions
- 1 domain
- 13 sequences

![Postgres DVD Rental ER Model](dvd-rental-sample-database-diagram.png)

## Development Environment Setup

### VS Code Intelisense for SQLAlchemy
These are PEP-484 typing stubs for SQLAlchemy 1.4 and 2.0. They are released concurrently along with a Mypy extension which is designed to work with these stubs, which assists primarily in the area of ORM mappings. The stubs replace the use of the [“sqlalchemy-stubs”](https://pypi.org/project/sqlalchemy2-stubs/) package published by Dropbox. Differences include that these stubs are generated against 1.4’s API as well as some adjustments to the use of generics


## Additional Tools
###  https://github.com/agronholm/sqlacodegen
This is a tool that reads the structure of an existing database and generates the appropriate SQLAlchemy model code, using the declarative style if possible.

This tool was written as a replacement for sqlautocode, which was suffering from several issues (including, but not limited to, incompatibility with Python 3 and the latest SQLAlchemy version).

## Contribution workflow
Here's how we suggest you to go about proposing a change to this project:
 
1. [Fork this project][fork] to your account.
2. [Create a branch][branch] for the change you intent to make.
3. Make your changes to your fork.
4. [Send a pull request][pr] from your fork's branch to our `main` branch.
 
[fork]: https://help.github.com/articles/fork-a-repo/
[branch]: https://help.github.com/articles/creating-and-deleting-branches-within-your-repository
[pr]: https://help.github.com/articles/using-pull-requests/
[coverage-quickstart]: https://coverage.readthedocs.io/en/coverage-5.5/#quick-start
 