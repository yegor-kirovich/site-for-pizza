import sqlalchemy
from data.Standart.db_session import SqlAlchemyBase


class Pizza(SqlAlchemyBase):
    __tablename__ = 'pizza'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    cost = sqlalchemy.Column(sqlalchemy.Integer,
                              index=True, nullable=True)
    dis_cost = sqlalchemy.Column(sqlalchemy.Integer,
                              index=True, nullable=True)
    href = sqlalchemy.Column(sqlalchemy.String, nullable=True)