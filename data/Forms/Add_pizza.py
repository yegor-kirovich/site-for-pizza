from flask_wtf import FlaskForm
from wtforms import BooleanField, RadioField, SubmitField, SelectMultipleField, widgets
from wtforms.validators import DataRequired
from data.Standart import db_session
from data.database.supplements_price import Supplements_price
from data.database.sauces_db import Sauces


db_session.global_init("db/pizzeria.db")


class MultiCheckBoxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class AddPizzaForm(FlaskForm):
    choices_supplements = []
    db_sess = db_session.create_session()
    for supplement in db_sess.query(Supplements_price).all():
        choices_supplements.append((str(supplement.id), f'{supplement.name} {supplement.cost} тг.'))

    choices_sauces = []
    for sauce in db_sess.query(Sauces).all():
        choices_sauces.append((sauce.name, sauce.name))

    size = RadioField('Размер', choices=[('small', 'Маленький'), ('medium', 'Средний'), ('big', 'Большой')],
                      validators=[DataRequired()])
    dough = RadioField('Тесто', choices=[('normal', 'Традиционное'), ('thin', 'Тонкое')],
                       validators=[(DataRequired())])
    supplements = MultiCheckBoxField('Добавки', choices=choices_supplements)
    sauces = MultiCheckBoxField('Соусы (Бесплатно)', choices=choices_sauces)
    submit = SubmitField('Добавить')
