from flask import Flask
from data import db_session
from forms.user import RegisterForm
from flask import render_template
from data.users import User
from data.tasks import Tasks
from flask import redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.loginform import LoginForm
from forms.TasksForm import TasksForm
from flask_restful import abort, Api
import task_resources

app = Flask(__name__)  # экземпляр класса Flask
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()  # инициализация LoginManager
login_manager.init_app(app)
api = Api(app)  # объект RESTful-AP


@app.route("/")
def index():
    db_sess = db_session.create_session()  # подключение БД
    if current_user.is_authenticated:  # проверка на авторизацию
        tasks = db_sess.query(Tasks).filter(Tasks.user_id == current_user.id)  # отображение дел данного пользователя
        return render_template("index.html", tasks=tasks)
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])  # страница регистрации
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()  # связь с БД
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)  # добавление пользователя в БД
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])  # страница входа в систему
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()  # связь с БД
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')  # выход из системы
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/tasks',  methods=['GET', 'POST'])  # добавление дел
@login_required
def add_tasks():
    form = TasksForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()  # связь с БД
        tasks = Tasks()
        tasks.user_id = current_user.id
        tasks.task = form.task.data
        tasks.commentary = form.commentary.data
        tasks.deadline = form.deadline.data
        db_sess.add(tasks)  # добавление дел в БД
        db_sess.commit()
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('task.html', title='Добавление дела',
                           form=form)


@app.route('/tasks/<int:id>', methods=['GET', 'POST'])  # изменение конкретного дела
@login_required
def edit_task(id):
    form = TasksForm()
    if request.method == "GET":
        db_sess = db_session.create_session()   # связь с БД
        tasks = db_sess.query(Tasks).filter(Tasks.id == id,
                                            ).first()
        if tasks:
            form.task.data = tasks.task
            form.commentary.data = tasks.commentary
            form.deadline.data = tasks.deadline
        else:
            abort(404)  # вызов ошибки при остутствии пользователя с данным id
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        tasks = db_sess.query(Tasks).filter(Tasks.id == id
                                            ).first()
        if tasks:
            tasks.task = form.task.data
            tasks.commentary = form.commentary.data
            tasks.deadline = form.deadline.data
            db_sess.commit()  # сохранение изменений
            return redirect('/')
        else:
            abort(404)
    return render_template('task.html',
                           title='Редактирование дела',
                           form=form
                           )


@app.route('/tasks_delete/<int:id>', methods=['GET', 'POST'])  # удаление конкретного дела
@login_required
def tasks_delete(id):
    db_sess = db_session.create_session()  # связь с БД
    tasks = db_sess.query(Tasks).filter(Tasks.id == id
                                        ).first()
    if tasks:
        db_sess.delete(tasks)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


def main():  # запуск приложения
    db_session.global_init("db/planner.db")
    api.add_resource(task_resources.TasksListResources, '/api/tasks')
    api.add_resource(task_resources.TasksResource, '/api/tasks/<int:tasks_id>')
    app.run()


if __name__ == '__main__':
    main()