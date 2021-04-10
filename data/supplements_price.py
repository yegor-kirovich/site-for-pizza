import sqlalchemy
from .db_session import SqlAlchemyBase


class Supplements_price(SqlAlchemyBase):
    __tablename__ = 'supplements'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    cost = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)