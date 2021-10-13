from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from app import db

from datetime import datetime
from flask_login import UserMixin
from app import login
from flask import current_app
import redis
from flask_table import Table, Col, ButtonCol, LinkCol, BoolCol
from flask_table.html import element
from sqlalchemy.dialects.postgresql import JSON

SCHEMA = 'debug'


class ResultsEMailSettings(Table):
    id = Col('id', show=False)
    id_owner = Col('id_owner', show=False)
    # spreadsheets_id = Col('spreadsheets_id')
    # credential_file = Col('credential_file')

    server_smpt = Col('server_smpt')
    server_imap = Col('server_imap')
    email = Col('email')
    port = Col('port')
    tls = Col('tls')
    delete = ButtonCol('Delete', 'delete_mail', url_kwargs=dict(id='id'))


# class myclass:
#     id = Col('id', show=False)
#     spreadsheets_id = Col('Pizdec')
#     # credential_file = Col('credential_file')
class RawCol(Col):
    """Class that will just output whatever it is given and will not
    escape it.
    """

    def td_format(self, content):
        return content


class ExternalURLCol(Col):
    url_google_spreadsheets = 'https://docs.google.com/spreadsheets/d/'

    def __init__(self, name, url_attr, **kwargs):
        self.url_attr = url_attr
        super(ExternalURLCol, self).__init__(name, **kwargs)



    def td_contents(self, item, attr_list):
        text = self.from_attr_list(item, attr_list)
        url = self.url_google_spreadsheets + self.from_attr_list(item, [self.url_attr])
        return element('a', {'href': url}, content=text)


class ResultsgoodleSS(Table):
    id = Col('id', show=True)
    #spreadsheets_id = Col('name')
    spreadsheets_id = ExternalURLCol('URL', url_attr='spreadsheets_id')
    #url = LinkCol('url google table', 'open_table', url_kwargs=dict(spreadsheets_id='spreadsheets_id'))
    #credential_file = Col('credential_file')
    delete = ButtonCol('Delete', 'delete_ss', url_kwargs=dict(id='id'))


class ResultsgoodleSSSingle(ResultsgoodleSS):
    delete = ButtonCol('Delete', 'delete_ss_single', url_kwargs=dict(id='id'))


class ResultsTask(Table):
    id = Col('id', show=True)
    desc = Col('Описание задачи')
    status = Col('status')
    datetime = Col('Время изменения задачи')
    spreadsheets_id = Col('GOOGLE spreadsheets_id')
    email = Col('email')
    delete = ButtonCol('Delete', 'delete_task', url_kwargs=dict(id='id'))
    start = ButtonCol('Start', 'update_task_status', url_kwargs=dict(id='id'))


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Report(db.Model):
    __table_args__ = {'schema': SCHEMA}
    __tablename__ = 'report'
    id = db.Column(db.Integer, primary_key=True)
    id_task = db.Column(db.Integer, db.ForeignKey('{}.listen_task.id'.format(SCHEMA)))
    id_user = db.Column(db.Integer, db.ForeignKey('{}.user.id'.format(SCHEMA)))
    status_complete = db.Column(db.Boolean, default=False)
    datetime = db.Column(db.DateTime, nullable=False)
    info = db.Column(JSON, nullable=True)


class EMailSettings(db.Model):
    __table_args__ = {'schema': SCHEMA}
    __tablename__ = 'email_settings'
    id_owner = db.Column(db.Integer, db.ForeignKey('{}.user.id'.format(SCHEMA)))
    id = db.Column(db.Integer, primary_key=True)
    server_smpt = db.Column(db.String(300))
    server_imap = db.Column(db.String(300))
    port = db.Column(db.Integer)
    tls = db.Column(db.Boolean)
    email = db.Column(db.String(300))
    email_default = db.Column(db.String(300))
    key_access_email = db.Column(db.String(300))

    def __repr__(self):
        return '<mail_settings {}>'.format(self.id)
    #
    # def set_mailpassword(self, password):
    #     self.mail_password_hash = generate_password_hash(password)
    #
    # def check_mailpassword(self, password):
    #     return check_password_hash(self.mail_password_hash, password)


class Spreadsheets(db.Model):
    __table_args__ = {'schema': SCHEMA}
    __tablename__ = 'spreadsheets'
    id = db.Column(db.Integer, primary_key=True)
    id_owner = db.Column(db.Integer, db.ForeignKey('{}.user.id'.format(SCHEMA)))
    spreadsheets_id = db.Column(db.String(300), nullable=False)
    credential_file = db.Column(JSON)

    def __repr__(self):
        return '<Spreadsheets {}>'.format(self.id)


class Message(db.Model):
    __table_args__ = {'schema': SCHEMA}
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('{}.user.id'.format(SCHEMA)))
    recipient_id = db.Column(db.Integer, db.ForeignKey('{}.user.id'.format(SCHEMA)))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message {}>'.format(self.body)


class ListenTask(db.Model):
    __table_args__ = {'schema': SCHEMA}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True, unique=True)
    desc = db.Column(db.String(256), nullable=False)
    datetime = db.Column(db.DateTime(), default=datetime.utcnow)
    status = db.Column(db.Boolean, default=False)
    folder = db.Column(db.String(256), nullable=False)
    id_email = db.Column(db.Integer, db.ForeignKey('{}.email_settings.id'.format(SCHEMA)))
    id_owner = db.Column(db.Integer, db.ForeignKey('{}.user.id'.format(SCHEMA)))
    id_spreadsheets = db.Column(db.Integer, db.ForeignKey('{}.spreadsheets.id'.format(SCHEMA)))
    reports = db.relationship('Report', backref='ListenTask', lazy='dynamic')

    def __repr__(self):
        return '<Listen {}>'.format(self.id)


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
    datetime = db.Column(db.DateTime(), default=datetime.utcnow)
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


class User(UserMixin, db.Model):
    __table_args__ = {'schema': SCHEMA}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    table_ss = db.relationship('Spreadsheets', backref='User', lazy='dynamic')
    emails = db.relationship('EMailSettings', backref='User', lazy='dynamic')
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    reports = db.relationship('Report', backref='User', lazy='dynamic')

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

# event.listen(db_session, 'after_flush', search.update_model_based_indexes)


# if __name__ == '__main__':
#     db.drop_all()
#     db.create_all()
#     db.session.add(User(username="Frank"))
#     db.session.commit()
#     app.run(debug=True)