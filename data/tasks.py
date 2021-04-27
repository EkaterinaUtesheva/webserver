import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


class Tasks(SqlAlchemyBase, SerializerMixin):  # модель для работы с таблицей tasks
    __tablename__ = 'tasks'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))

    task = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    commentary = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    deadline = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user = orm.relation('User')