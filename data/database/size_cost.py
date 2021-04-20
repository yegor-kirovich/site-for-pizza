import sqlalchemy
from data.Standart.db_session import SqlAlchemyBase


class Size_cost(SqlAlchemyBase):
    __tablename__ = 'size_cost'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    big_size = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    med_size = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    small_size = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    big_size_dis = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    med_size_dis = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    small_size_dis = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
