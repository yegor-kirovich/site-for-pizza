from flask import Flask, render_template, session, redirect, url_for
from data import db_session
from data.pizza import Pizza
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data.user import User
from data.orders import Orders
from data.Forms.Login import LoginForm
from data.Forms.Registration import RegisterForm

db_session.global_init("db/pizzeria.db")

from data.Forms.Add_pizza import AddPizzaForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def main_menu():
    db_sess = db_session.create_session()
    pizza = db_sess.query(Pizza)
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    short = "static/img/"
    if session['visits_count'] > 10:
        return render_template("main.html", pizza=pizza,
                               short=short, discount=1)
    return render_template("main.html", pizza=pizza, short=short, discount=0)


@app.route('/add_pizza/<int:pizza_id>', methods=['GET', 'POST'])
def add_pizza(pizza_id):
    form = AddPizzaForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if current_user.is_authenticated:
            orders = Orders()
            orders.pizza_id = pizza_id
            orders.size = form.size.data
            orders.dough = form.dough.data
            orders.supplements = ', '.join(form.supplements.data)
            orders.sauces = ', '.join(form.sauces.data)
            current_user.orders.append(orders)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/')
        else:
            orders = session.get('orders', [])
            orders.append({'pizza_id': pizza_id,
                           'size': form.size.data,
                           'dough': form.dough.data,
                           'supplements': form.supplements.data,
                           'sauces': form.sauces.data})
            session['orders'] = orders

            return redirect('/')

    db_sess = db_session.create_session()
    pizza = db_sess.query(Pizza).get(pizza_id)
    return render_template('add_pizza.html', pizza_img=url_for('static', filename=f'img/{pizza.href}'),
                           form=form, alt=pizza.name)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    app.run()
