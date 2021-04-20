import sqlalchemy
from data.Standart.db_session import SqlAlchemyBase


class Sauces(SqlAlchemyBase):
    __tablename__ = 'sauces'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)