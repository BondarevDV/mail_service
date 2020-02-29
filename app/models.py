from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from app import db

from datetime import datetime
from flask_login import UserMixin
from app import login
from flask import current_app
import redis
from flask_table import Table, Col, ButtonCol, LinkCol, BoolCol
from sqlalchemy.dialects.postgresql import JSON

SCHEMA = 'mail'


class ResultsMailSettings(Table):
    id = Col('id', show=False)
    # spreadsheets_id = Col('spreadsheets_id')
    # credential_file = Col('credential_file')

    server_smpt = Col('server_smpt')
    server_imap = Col('server_imap')
    email = Col('email')
    port = Col('port')
    tls = Col('tls')
    delete = ButtonCol('Delete', 'delete_mail', url_kwargs=dict(id='id'))

class ResultsgoodleSS(Table):
    id = Col('id', show=False)
    spreadsheets_id = Col('spreadsheets_id')
    credential_file = Col('credential_file')




@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class MailSettings(db.Model):
    __table_args__ = {'schema': SCHEMA}
    id = db.Column(db.Integer, primary_key=True)
    server_smpt = db.Column(db.String(300))
    server_imap = db.Column(db.String(300))
    port = db.Column(db.Integer)
    tls = db.Column(db.Boolean)
    email = db.Column(db.String(300))
    email_default = db.Column(db.String(300))
    mail_password_hash = db.Column(db.String(300))

    def __repr__(self):
        return '<mail_settings {}>'.format(self.body)

    def set_mailpassword(self, password):
        self.mail_password_hash = generate_password_hash(password)

    def check_mailpassword(self, password):
        return check_password_hash(self.mail_password_hash, password)


class Spreadsheets(db.Model):
    __table_args__ = {'schema': SCHEMA}
    id = db.Column(db.Integer, primary_key=True)
    spreadsheets_id = db.Column(db.String(300), index=True, unique=True, nullable=False)
    credential_file = db.Column(JSON)

    def __repr__(self):
        return '<Spreadsheets {}>'.format(self.body)


class Listen(db.Model):
    __table_args__ = {'schema': SCHEMA}
    id = db.Column(db.Integer, primary_key=True)
    id_mail = db.Column(db.Integer, db.ForeignKey('{}.mail_settings.id'.format(SCHEMA)))
    id_user = db.Column(db.Integer, db.ForeignKey('{}.user.id'.format(SCHEMA)))
    #id_spreadsheets = db.Column(db.Integer, db.ForeignKey('Spreadsheets.id'))

    def __repr__(self):
        return '<Listen {}>'.format(self.body)


class Message(db.Model):
    __table_args__ = {'schema': SCHEMA}
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('{}.user.id'.format(SCHEMA)))
    recipient_id = db.Column(db.Integer, db.ForeignKey('{}.user.id'.format(SCHEMA)))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message {}>'.format(self.body)


class User(UserMixin, db.Model):
    __table_args__ = {'schema': SCHEMA}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def launch_task(self, name, description, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue('app.tasks.' + name, self.id,
                                                *args, **kwargs)
        task = Task(id=rq_job.get_id(), name=name, description=description,
                    user=self)
        db.session.add(task)
        return task

    def get_tasks_in_progress(self):
        return Task.query.filter_by(user=self, complete=False).all()

    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, user=self,
                                    complete=False).first()


class Post(db.Model):
    __table_args__ = {'schema': SCHEMA}
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('{}.user.id'.format(SCHEMA)))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Task(db.Model):
    __table_args__ = {'schema': SCHEMA}
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    status = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('{}.user.id'.format(SCHEMA)))
    complete = db.Column(db.Boolean, default=False)

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100

