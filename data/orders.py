import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Orders(SqlAlchemyBase):
    __tablename__ = 'orders'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    pizza_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    size = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    dough = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    supplements = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    sauces = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey('users.id'))

    user = orm.relation('User')
