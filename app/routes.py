# -*- coding: utf-8 -*-
from dominate.tags import form

from app import app
from app import db
from app import mail
from app.forms import LoginForm
from app.forms import MessageForm
from app.forms import NameForm
from app.forms import RegistrationForm, LoadForm, SaveMailSettingsForm, spreadsheetForm
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, MailSettings, ResultsMailSettings, Spreadsheets
from werkzeug.utils import secure_filename
import json

import os
from flask_mail import Message
import service_mail
from flask import abort
from flask import redirect
from config import config
from app import celery
from celery.result import AsyncResult

from threading import Thread

# @app.route('/index_1')
# def index():
#     user = {'username': 'Эльдар Рязанов'}
#     posts = [
#         {
#             'author': {'username': 'John'},
#             'body': 'Beautiful day in Portland!'
#         },
#         {
#             'author': {'username': 'Susan'},
#             'body': 'The Avengers movie was so cool!'
#         },
#         {
#             'author': {'username': 'Ипполит'},
#             'body': 'Какая гадость эта ваша заливная рыба!!'
#         }
#     ]
#     return render_template('index_1.html', title='Home', user=user, posts=posts)


class load_user:
    def __init__(self, id):
        self.users = dict()
        self.users['1'] = 'Dima'
        self.users['2'] = 'Anna'
        self.user = self.users.get(id, None)
        if self.user is None:
            return None
        print(self.user)

    @property
    def name(self):
        return self.user


@app.route('/process/<name>')
def process(name):
    return name


@app.route('/test_user/<id>')
def get_user(id):
    user = load_user(id)
    if not user:
        abort(404)
    return '<h1>Hello, %s </h1>' % user.name


@app.route('/input/')
def input():
    return render_template('message.html')


@app.route('/user/')
def user():
    form = personalAccount()
    form.email.label = "New email"
    return render_template('room.html', form=form, name='LALALA')


@app.route('/book', methods=['GET', 'POST'])
def book():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
    form.name.data = ''
    return render_template('book_index.html', form=form, name=name)


@app.route('/test_redirect')
def test_redirect():
    return redirect('http://www.example.com')


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Эльдар Рязанов'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        },
        {
            'author': {'username': 'Ипполит'},
            'body': 'Какая гадость эта ваша заливная рыба!!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    print('login')
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('room'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/send-mail/')
def send_mail():
    msg = Message("Hello", sender="d.bondarev.86@yandex.ru", recipients=["d.bondarev.86@yandex.ru"])
    msg.body = "Yo!\nHave you heard the good word of Python???"
    # You can set the recipient emails immediately, or individually:

    # assert msg.sender == "Me <me@example.com> d.bondarev.86@yandex.ru"
    mail.send(msg)
    return 'Mail sent!'


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# @app.route('/room', methods=['GET', 'POST'])
# @login_required
# def room():
#     #flash('Congratulations, user enter in room!')
#     form = SaveMailSettingsForm()
#     return render_template('room.html', title='room', form=form)


@app.route('/room', methods=['GET', 'POST'])
@login_required
#@login_manager.user_loader
def room():
    form = SaveMailSettingsForm()
    form_googlesheets = spreadsheetForm()
    items = db.session.query(MailSettings)
    table = ResultsMailSettings(items)
    table.border = True
    # username=getattr(current_user, 'username', 'unknown'))
    # username=current_user.username)
    user = User.query.filter_by(id=current_user.id).first()
    # if form.is_submitted():
    #     print('Room validate_on_submit form')
    #     mail_settings = MailSettings(server_imap=form.server_imap.data,
    #                                  server_smpt=form.server_smpt.data,
    #                                  port=587,
    #                                  tls=True,
    #                                  email=form.email.data,
    #                                  email_default=form.email.data)
    #     mail_settings.set_mailpassword(form.mail_password.data)
    #     db.session.add(mail_settings)
    #     db.session.commit()
    #     flash('Congratulations, you are now a registered user!')
    #     return redirect(url_for('room'))
    if form_googlesheets.is_submitted():
        print('Room validate_on_submit form_googlesheets ')
        print(form_googlesheets.spreadsheets_id.data)
        data = json.load(form_googlesheets.credential_file.data)
        ss_settings = Spreadsheets(spreadsheets_id=form_googlesheets.spreadsheets_id.data,
                                   credential_file=data)
        # mail_settings.set_mailpassword(form.mail_password.data)
        db.session.add(ss_settings)
        db.session.commit()
        flash('Congratulations, you are add google sheets!')
        return redirect(url_for('room'))

    return render_template('room.html',
                           title='room',
                           form_mail=form,
                           form_gs=form_googlesheets,
                           table=table,
                           user=user)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/load', methods=['GET', 'POST'])
@login_required
def load():
    form = LoadForm()
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('index'))
    return render_template('load.html', title='load', form=form)


@celery.task(name='spreadsheets.processing')
def processing(filename):
    while True:
        params = config()
        spreadsheetId = params.get('spreadsheetid', None)
        GOOGLE_CREDENTIALS_FILE = params.get('credential_file', None)
        if spreadsheetId is not None:
            service_mail.main(spreadsheetId, GOOGLE_CREDENTIALS_FILE)


@app.route('/process/<filename>')
def task_processing(filename):
    task = processing.delay(filename)
    async_result = AsyncResult(id=task.task_id, app=celery)
    processing_result = async_result.get()
    return processing_result


@app.route('/start/<cmd>', methods=['GET', 'POST'])
@login_required
def run(cmd):
    while cmd:
        print(cmd)
        params = config()
        spreadsheetId = params.get('spreadsheetid', None)
        GOOGLE_CREDENTIALS_FILE = params.get('credential_file', None)
        if spreadsheetId is not None:
            service_mail.main(spreadsheetId, GOOGLE_CREDENTIALS_FILE)


@app.route('/contact/', methods=['GET', 'POST'])
def contact():
    # ...
    # db.session.commit()
    email = "d.bondarev.86@yandex.ru"
    name = "Dmitry"
    msg = Message("Feedback", recipients=[app.config['MAIL_USERNAME']])
    msg.body = "You have received a new feedback from {} <{}>.".format(name, email)
    mail.connect()
    mail.send(msg)

    print("\nData received. Now redirecting ...")
    return redirect(url_for('index'))
