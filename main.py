from flask import Flask, render_template, session, redirect, url_for, abort
from dotenv import load_dotenv
from mail_sender import send_mail
from data.Standart import db_session
from data.database.pizza import Pizza
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data.database.user import User
from data.database.pizza_orders import Pizza_orders
from data.database.supplements_price import Supplements_price
from data.database.size_cost import Size_cost
from data.Forms.Login import LoginForm
from data.Forms.Registration import RegisterForm
from data.Forms.Add_pizza import AddPizzaForm
from data.Forms.Get_user_info import EmailForm
from data.Forms.Admin_Rights import AdminPizzaForm
from data.database.snacks import Snack
from data.database.snacks_orders import Snacks_orders

db_session.global_init("db/pizzeria.db")

app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY'] = 'pizzeria_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

dis = False


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def main_menu():
    global dis
    db_sess = db_session.create_session()
    pizza = db_sess.query(Pizza)
    snack = db_sess.query(Snack)
    short = "static/img/"
    if current_user.is_authenticated and (current_user.count_orders % 10 == 0):
        dis = True
        return render_template("main.html", pizza=pizza,
                               short=short, discount=1, snack=snack, title='Пиццерия')
    dis = False
    return render_template("main.html", pizza=pizza, short=short, discount=0, snack=snack, title='Пиццерия')


@app.route('/add_pizza/<int:pizza_id>', methods=['GET', 'POST'])
def add_pizza(pizza_id):
    form = AddPizzaForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if current_user.is_authenticated:
            pizza_orders = Pizza_orders()
            pizza_orders.pizza_id = pizza_id
            pizza_orders.size = form.size.data
            pizza_orders.dough = form.dough.data
            pizza_orders.supplements = ', '.join(form.supplements.data)
            pizza_orders.sauces = ', '.join(form.sauces.data)
            current_user.pizza_orders.append(pizza_orders)
            db_sess.merge(current_user)
            db_sess.commit()
        else:
            orders = session.get('orders', {'pizzas': [],
                                            'snacks': []})
            orders['pizzas'].append({'pizza_id': pizza_id,
                                     'size': form.size.data,
                                     'dough': form.dough.data,
                                     'supplements': form.supplements.data,
                                     'sauces': form.sauces.data})
            session['orders'] = orders
        return redirect('/')
    db_sess = db_session.create_session()
    pizza = db_sess.query(Pizza).get(pizza_id)
    return render_template('add_pizza.html', pizza_img=url_for('static', filename=f'img/pizzas/{pizza.href}'),
                           form=form, alt=pizza.name, title='Добавление пиццы')


@app.route('/add_snack/<int:snack_id>')
def add_snack(snack_id):
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        order_snack = Snacks_orders()
        order_snack.snack_id = snack_id
        current_user.snacks_orders.append(order_snack)
        db_sess.merge(current_user)
        db_sess.commit()
    else:
        orders = session.get('orders', {'pizzas': [],
                                        'snacks': []})
        orders['snacks'].append({'snack_id': snack_id})
        session['orders'] = orders
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
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
            email=form.email.data,
            phone_number=form.phone_number.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/profile')
def profile_page():
    return render_template('profile.html', title='Профиль',
                           user_name=current_user.name, user_email=current_user.email,
                           user_count_orders=current_user.count_orders)


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
                               form=form, title='Авторизация')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/send_mail', methods=['GET', 'POST'])
def send_check():
    global dis

    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        address = db_sess.query(User).get(current_user.id).address
        email = db_sess.query(User).get(current_user.id).email
        pizzas_order = db_sess.query(Pizza_orders).filter(Pizza_orders.user_id == current_user.id)
        total_cost = 0
        text = 'Чек'
        for i in pizzas_order:
            pizza = db_sess.query(Pizza).get(i.pizza_id)
            size_pizza_cost = db_sess.query(Size_cost).get(pizza.id)

            if i.size == 'small':
                size = 'Маленький'
                if dis:
                    total_cost += size_pizza_cost.small_size_dis
                    pizza_cost = size_pizza_cost.small_size_dis
                else:
                    total_cost += size_pizza_cost.small_size
                    pizza_cost = size_pizza_cost.small_size
            elif i.size == 'medium':
                size = 'Средний'
                if dis:
                    total_cost += size_pizza_cost.med_size_dis
                    pizza_cost = size_pizza_cost.med_size_dis
                else:
                    total_cost += size_pizza_cost.med_size
                    pizza_cost = size_pizza_cost.med_size
            elif i.size == 'big':
                size = 'Большой'
                if dis:
                    total_cost += size_pizza_cost.big_size_dis
                    pizza_cost = size_pizza_cost.big_size_dis
                else:
                    total_cost += size_pizza_cost.big_size
                    pizza_cost = size_pizza_cost.big_size

            if i.dough == 'normal':
                dough = 'Традиционное'
            elif i.dough == 'thin':
                dough = 'Тонкое'

            text += f'\n---------------------------------------\nПицца: {pizza.name}\nРазмер: {size}\n' \
                    f'Тесто: {dough}\nЦена: {pizza_cost} тенге'

            if i.supplements:
                text += '\n\nДобавки:\n\n'
                supplements = []
                for j in i.supplements.split(', '):
                    supple = db_sess.query(Supplements_price).get(int(j))
                    supplements.append(f'{supple.name} - {supple.cost} тг.')
                    total_cost += supple.cost
                text += '\n'.join(supplements)

            if i.sauces:
                text += f'\n\nСоусы: {i.sauces}'

        text += '\n---------------------------------------'

        snacks = []
        drinks = []
        snacks_order = db_sess.query(Snacks_orders).filter(Snacks_orders.user_id == current_user.id)
        for i in snacks_order:
            snack = db_sess.query(Snack).get(i.snack_id)
            if snack.type == 'snack':
                if dis:
                    total_cost += snack.dis_cost
                    snacks.append(f'{snack.name} - {snack.dis_cost} тг.')
                else:
                    total_cost += snack.cost
                    snacks.append(f'{snack.name} - {snack.cost} тг.')
            elif snack.type == 'drink':
                if dis:
                    total_cost += snack.dis_cost
                    snacks.append(f'{snack.name} - {snack.dis_cost} тг.')
                else:
                    total_cost += snack.cost
                    snacks.append(f'{snack.name} - {snack.cost} тг.')

        if snacks:
            snacks = '\n'.join(snacks)
            text += f'\nЗакуски:\n\n{snacks}\n---------------------------------------'
        if drinks:
            drinks = '\n'.join(drinks)
            text += f'\nНапитки:\n\n{drinks}\n---------------------------------------'

        text += f'\nИтого: {total_cost} тенге\n\nВаш заказ будет доставлен по адресу: {address}\nПриятного аппетита!'
        if send_mail(email, 'Спасибо за заказ!', text):
            dis = False
            current_user.count_orders += 1
            db_sess.merge(current_user)

            curr_user_pizza_orders = db_sess.query(Pizza_orders).filter(Pizza_orders.user_id == current_user.id)
            for i in curr_user_pizza_orders:
                db_sess.delete(i)

            curr_user_snacks_orders = db_sess.query(Snacks_orders).filter(Snacks_orders.user_id == current_user.id)
            for i in curr_user_snacks_orders:
                db_sess.delete(i)

            db_sess.commit()
            return redirect('/')
        return f'При отправке сообщения на адрес {email} произошла ошибка<br><a href="http://127.0.0.1:5000/">На ' \
               f'главную</a>'
    else:
        form = EmailForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            total_cost = 0
            text = 'Чек'
            for i in session['orders']['pizzas']:
                pizza = db_sess.query(Pizza).get(i['pizza_id'])
                size_pizza_cost = db_sess.query(Size_cost).get(pizza.id)

                if i['size'] == 'small':
                    size = 'Маленький'
                    total_cost += size_pizza_cost.small_size
                    pizza_cost = size_pizza_cost.small_size
                elif i['size'] == 'medium':
                    size = 'Средний'
                    total_cost += size_pizza_cost.med_size
                    pizza_cost = size_pizza_cost.med_size
                elif i['size'] == 'big':
                    size = 'Большой'
                    total_cost += size_pizza_cost.big_size
                    pizza_cost = size_pizza_cost.big_size

                if i['dough'] == 'normal':
                    dough = 'Традиционное'
                elif i['dough'] == 'thin':
                    dough = 'Тонкое'

                text += f'\n---------------------------------------\nПицца: {pizza.name}\nРазмер: {size}\n' \
                        f'Тесто: {dough}\nЦена: {pizza_cost} тенге'

                if i['supplements']:
                    text += '\n\nДобавки:\n\n'
                    supplements = []
                    for j in i['supplements']:
                        supple = db_sess.query(Supplements_price).get(int(j))
                        supplements.append(f'{supple.name} - {supple.cost} тг.')
                        total_cost += supple.cost
                    text += '\n'.join(supplements)

                if i['sauces']:
                    sauces = ', '.join(i['sauces'])
                    text += f'\n\nСоусы: {sauces}'

            text += '\n---------------------------------------'

            snacks = []
            drinks = []
            for i in session['orders']['snacks']:
                snack = db_sess.query(Snack).get(i['snack_id'])
                if snack.type == 'snack':
                    snacks.append(f'{snack.name} - {snack.cost} тг.')
                    total_cost += snack.cost
                elif snack.type == 'drink':
                    drinks.append(f'{snack.name} - {snack.cost} тг.')
                    total_cost += snack.cost

            if snacks:
                snacks = '\n'.join(snacks)
                text += f'\nЗакуски:\n\n{snacks}\n---------------------------------------'
            if drinks:
                drinks = '\n'.join(drinks)
                text += f'\nНапитки:\n\n{drinks}\n---------------------------------------'

            text += f'\nИтого: {total_cost} тенге\n\nВаш заказ будет доставлен по адресу: {form.address.data}' \
                    f'\nПриятного аппетита!'

            if send_mail(form.email.data, 'Спасибо за заказ!', text):
                session['orders'] = {'pizzas': [],
                                     'snacks': []}
                return redirect('/')
            return f'При отправке сообщения на адрес {form.email.data} произошла ошибка<br><a ' \
                   f'href="http://127.0.0.1:5000/">На главную</a>'
        return render_template('get_user_info.html', form=form, title='Оформление заказа')


@app.route('/basket')
def basket():
    db_sess = db_session.create_session()
    short = "static/img/"
    if current_user.is_authenticated:
        pizza_list = []
        snack_list = []
        if "orders" in session:
            if session["orders"]["pizzas"]:
                pizzas = db_sess.query(Pizza_orders)
                a = []
                for i in pizzas:
                    a.append(i.id)
                if not a:
                    b = 0
                else:
                    b = a[-1] + 1
                for i in range(len(session["orders"]["pizzas"])):
                    pizza = Pizza_orders()
                    pizza.id = b + i
                    pizza_info = session["orders"]
                    pizza.pizza_id = pizza_info["pizzas"][i]["pizza_id"]
                    pizza.size = pizza_info["pizzas"][i]["size"]
                    pizza.dough = pizza_info["pizzas"][i]["dough"]
                    pizza.supplements = ", ".join(pizza_info["pizzas"][i]["supplements"])
                    pizza.sauces = ", ".join(pizza_info["pizzas"][i]["sauces"])
                    pizza.user_id = current_user.id
                    db_sess.add(pizza)
                    db_sess.commit()
                orders = session.get('orders', {'pizzas': [],
                                                'snacks': []})
                orders['pizzas'] = []
                session['orders'] = orders

                if session["orders"]["snacks"]:
                    snacks = db_sess.query(Snacks_orders)
                    a = []
                    for i in snacks:
                        a.append(i.id)
                    if not a:
                        b = 0
                    else:
                        b = a[-1] + 1
                    for i in range(len(session["orders"]["snacks"])):
                        snack = Snacks_orders()
                        snack.id = b + i
                        snack_info = session["orders"]
                        snack.snack_id = snack_info["snacks"][i]["snack_id"]
                        snack.user_id = current_user.id
                        db_sess.add(snack)
                        db_sess.commit()
                    orders = session.get('orders', {'pizzas': [],
                                                    'snacks': []})
                    orders['snacks'] = []
                    session['orders'] = orders

        for pizza in db_sess.query(Pizza_orders).filter(Pizza_orders.user_id == current_user.id):
            for i in db_sess.query(Pizza).filter(Pizza.id == pizza.pizza_id):
                supl = []
                sum = 0
                costs = db_sess.query(Size_cost).filter(Size_cost.id == i.id).first()
                if pizza.supplements != "":
                    for j in pizza.supplements.split(", "):
                        sup = db_sess.query(Supplements_price).filter(Supplements_price.id == j).first()
                        sum += sup.cost
                        supl.append(sup.name)
                if not dis:
                    pizza_list.append((i, pizza, ", ".join(supl), [costs.small_size + sum, costs.med_size + sum,
                                                                   costs.big_size + sum]))
                else:
                    pizza_list.append((i, pizza, ", ".join(supl), [costs.small_size_dis + sum, costs.med_size_dis + sum,
                                                                   costs.big_size_dis + sum]))
        for snack in db_sess.query(Snacks_orders).filter(Snacks_orders.user_id == current_user.id):
            for i in db_sess.query(Snack).filter(Snack.id == snack.snack_id):
                snack_list.append((i, snack.id))

        if not pizza_list and not snack_list:
            basket_is_empty = True
        else:
            basket_is_empty = False

        return render_template('basket.html', pizza=pizza_list, short=short, snack=snack_list, log=1, title="Корзина",
                               basket_is_empty=basket_is_empty, dis=dis)
    else:
        list_pizza = []
        list_snack = []
        if 'orders' in session:
            pizza = session["orders"]["pizzas"]
            snack = session["orders"]["snacks"]
            a = -1
            for i in pizza:
                a += 1
                p = db_sess.query(Pizza).filter(Pizza.id == i["pizza_id"]).first()
                sum = 0
                supl = []
                for j in i["supplements"]:
                    sup = db_sess.query(Supplements_price).filter(Supplements_price.id == j).first()
                    sum += sup.cost
                    supl.append(sup.name)
                costs = db_sess.query(Size_cost).filter(Size_cost.id == p.id).first()
                list_pizza.append([i, p, ", ".join(supl), a, [costs.small_size + sum, costs.med_size + sum,
                                                              costs.big_size + sum]])
            a = -1
            for i in snack:
                a += 1
                p = db_sess.query(Snack).filter(Snack.id == i["snack_id"]).first()
                list_snack.append([i, p, a])

        if not list_pizza and not list_snack:
            basket_is_empty = True
        else:
            basket_is_empty = False

        return render_template('basket.html', pizza=list_pizza, snack=list_snack, short=short, log=0, title="Корзина",
                               basket_is_empty=basket_is_empty)


@app.route('/delete/<string:type>/<int:id>', methods=['GET', 'POST'])
def item_delete(type, id):
    db_sess = db_session.create_session()
    if type == "pizza":
        pizza = db_sess.query(Pizza_orders).filter(Pizza_orders.id == id).first()
        if pizza:
            db_sess.delete(pizza)
            db_sess.commit()
        else:
            abort(404)
        return redirect('/basket')
    if type == "snack":
        snack = db_sess.query(Snacks_orders).filter(Snacks_orders.id == id).first()
        if snack:
            db_sess.delete(snack)
            db_sess.commit()
        else:
            abort(404)
        return redirect('/basket')


@app.route('/delete_log/<string:type>/<int:id>', methods=['GET', 'POST'])
def delete_log(id, type):
    if type == "pizza":
        orders = session.get('orders', {'pizzas': [],
                                        'snacks': []})
        del orders["pizzas"][id]
        session['orders'] = orders
    else:
        orders = session.get('orders', {'pizzas': [],
                                        'snacks': []})
        del orders["snacks"][id]
        session['orders'] = orders
    return redirect('/basket')


@app.route('/add_num/<int:id>')
def add_num(id):
    global a
    a[id] += 1
    return redirect('/')


@app.route('/delete_num/<int:id>')
def delete_num(id):
    global a
    if a[id] != 1:
        a[id] -= 1
    return redirect('/')


@app.route('/admin_profile', methods=['GET', 'POST'])
def admin_profile_page():
    if current_user.is_authenticated:
        if current_user.name != 'admin':
            return redirect('/')
    else:
        return redirect('/')
    form = AdminPizzaForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if form.type.data == 'pizzas':
            pizza = db_sess.query(Pizza)
            a = list()
            for i in pizza:
                a.append(i.id)
            if not a:
                b = 0
            else:
                b = a[-1] + 1
            pizza_cost = Size_cost()
            pizza_cost.id = b
            pizza_cost.med_size = form.cost.data
            pizza_cost.small_size = int(form.cost.data) - 1000
            pizza_cost.big_size = int(form.cost.data) + 1000
            pizza_cost.med_size_dis = form.cost.data * 0.9
            pizza_cost.small_size_dis = (int(form.cost.data) - 1000) * 0.9
            pizza_cost.big_size_dis = (int(form.cost.data) + 1000) * 0.9
            pizza = Pizza()
            pizza.id = b
            pizza.name = form.name.data
            pizza.cost = form.cost.data
            pizza.dis_cost = form.cost.data * 0.9
            pizza.about = form.about.data
            f = form.photo.data.read()
            with open(f'static/img/{form.type.data}/{form.name.data}.jpg', 'wb') as i:
                i.write(f)
            pizza.href = f'{form.name.data}.jpg'
            db_sess.merge(pizza)
        elif form.type.data == 'snacks':
            snack = db_sess.query(Snack)
            a = list()
            for i in snack:
                a.append(i.id)
            if not a:
                b = 0
            else:
                b = a[-1] + 1
            snack = Snack()
            snack.id = b
            snack.name = form.name.data
            snack.cost = form.cost.data
            snack.dis_cost = form.cost.data * 0.9
            snack.about = form.about.data
            snack.type = 'snack'
            f = form.photo.data.read()
            with open(f'static/img/{form.type.data}/{form.name.data}.jpg', 'wb') as i:
                i.write(f)
            snack.href = f'{form.name.data}.jpg'
            db_sess.merge(snack)
        elif form.type.data == 'drinks':
            snack = db_sess.query(Snack)
            a = list()
            for i in snack:
                a.append(i.id)
            if not a:
                b = 0
            else:
                b = a[-1] + 1
            snack = Snack()
            snack.id = b
            snack.name = form.name.data
            snack.cost = form.cost.data
            snack.dis_cost = form.cost.data * 0.9
            snack.about = form.about.data
            snack.type = 'drink'
            f = form.photo.data.read()
            with open(f'static/img/{form.type.data}/{form.name.data}.jpg', 'wb') as i:
                i.write(f)
            snack.href = f'{form.name.data}.jpg'
            db_sess.merge(snack)
        db_sess.commit()
        return redirect("/")
    return render_template('admin.html', title='Профиль Админа', form=form)


@app.route('/about')
def about():
    return render_template('map.html', title='Про нас')


@app.route('/delete_bd/<string:type>/<int:id>')
def delete_bd(type, id):
    db_sess = db_session.create_session()
    if type == "pizza":
        pizza = db_sess.query(Pizza).filter(Pizza.id == id).first()
        if pizza:
            db_sess.delete(pizza)
            db_sess.commit()
        else:
            abort(404)
        return redirect('/')
    if type == "snack":
        snack = db_sess.query(Snack).filter(Snack.id == id).first()
        if snack:
            db_sess.delete(snack)
            db_sess.commit()
        else:
            abort(404)
        return redirect('/')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    app.run()
