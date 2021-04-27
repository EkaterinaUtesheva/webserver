from flask_restful import reqparse, abort, Api, Resource
from data import db_session
from data.tasks import Tasks
from flask import jsonify


def abort_if_tasks_not_found(task_id):
    session = db_session.create_session()
    tasks = session.query(Tasks).get(task_id)
    if not tasks:
        abort(404, message=f"Task {task_id} not found")


class TasksResource(Resource):
    def get(self, tasks_id):
        abort_if_tasks_not_found(tasks_id)
        session = db_session.create_session()
        tasks = session.query(Tasks).get(tasks_id)
        return jsonify({'tasks': tasks.to_dict(
                        only = ('id', 'task', 'user_id', 'commentary', 'deadline'))})

    def delete(self, tasks_id):
        abort_if_tasks_not_found(tasks_id)
        session = db_session.create_session()
        tasks = session.query(Tasks).get(tasks_id)
        session.delete(tasks)
        session.commit()
        return jsonify({'success': 'OK'})


class TasksListResources(Resource):
    def get(self):
        session = db_session.create_session()
        tasks = session.query(Tasks).all()
        return jsonify({'tasks': [item.to_dict(
                        only = ('id', 'task', 'user_id', 'commentary', 'deadline')) for item in tasks]})

    def post(self):
        parser = reqparse.RequestParser()
        args = parser.parse_args()
        session = db_session.create_session()
        tasks = Tasks(
            id = args['id'],
            task = args['task'],
            user_id = args['user_id'],
            commentary = args['commentary'],
            deadline = args['deadline']
        )
        session.add(tasks)
        session.commit()
        return jsonify({'success': 'OK'})