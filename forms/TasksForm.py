from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms import SubmitField


class TasksForm(FlaskForm):  # форма для работы с делами
    task = TextAreaField("Дело")
    commentary = TextAreaField("Комментарий")
    deadline = TextAreaField("Срок сдачи")
    submit = SubmitField('Применить')