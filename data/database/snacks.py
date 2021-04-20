import sqlalchemy
from data.Standart.db_session import SqlAlchemyBase


class Snack(SqlAlchemyBase):
    __tablename__ = 'snack'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    cost = sqlalchemy.Column(sqlalchemy.Integer,
                             index=True, nullable=True)
    dis_cost = sqlalchemy.Column(sqlalchemy.Integer,
                                 index=True, nullable=True)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    href = sqlalchemy.Column(sqlalchemy.String, nullable=True)
