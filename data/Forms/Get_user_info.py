from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField


class EmailForm(FlaskForm):
    email = EmailField('Введите почту', validators=[DataRequired()])
    phone_number = StringField('Введите номер телефона', validators=[DataRequired()])
    address = StringField('Введите адрес', validators=[DataRequired()])
    submit = SubmitField('Отправить')
