from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired
from data.Standart import db_session


db_session.global_init("db/pizzeria.db")


class AdminPizzaForm(FlaskForm):
    type = RadioField('Продукт', choices=[('snacks', 'Снэк'), ('pizzas', 'Пицца'), ('drinks', "Напиток")],
                      validators=[DataRequired()])
    name = StringField('Название продукта', validators=[DataRequired()])
    cost = IntegerField('Цена', validators=[DataRequired()])
    about = StringField('Информация', validators=[DataRequired()])
    photo = FileField('Изображение продукта', validators=[FileRequired()])
    submit = SubmitField('Добавить')