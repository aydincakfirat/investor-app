"""
SQLAlchemy declarative base.
All ORM models must import and extend Base from this module
so that Alembic can discover them via autogenerate.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
