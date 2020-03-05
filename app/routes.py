# -*- coding: utf-8 -*-
from dominate.tags import form

from app import app
from app import db
from app import mail
from app.forms import LoginForm
from app.forms import MessageForm
from app.forms import NameForm
from app.forms import RegistrationForm, LoadForm, SaveMailSettingsForm, spreadsheetForm, ConfigListenForm
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, MailSettings, ResultsMailSettings, Spreadsheets, ResultsgoodleSS, ListenTask
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


@app.route('/process/<name>')
def process(name):
    return name


@app.route('/user/')
def user():
    form = personalAccount()
    form.email.label = "New email"
    return render_template('room.html', form=form, name='LALALA')





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


@app.route('/delete_mail/<id>', methods=['GET', 'POST'])
@login_required
def delete_mail(id):
    print('remove = ', id)
    form = SaveMailSettingsForm()
    form_googlesheets = spreadsheetForm()
    form_listen = ConfigListenForm()
    mail = MailSettings.query.get(id)
    db.session.delete(mail)
    db.session.commit()

    items = db.session.query(MailSettings)
    table = ResultsMailSettings(items)
    table.border = True

    items_ss = db.session.query(Spreadsheets)
    table_ss = ResultsgoodleSS(items_ss)
    table_ss.border = True
    user = User.query.filter_by(id=current_user.id).first()

    return render_template('room.html',
                           title='room',
                           form_mail=form,
                           form_gs=form_googlesheets,
                           form_l=form_listen,
                           table=table,
                           table_ss=table_ss,
                           user=user)


@app.route('/delete_ss/<id>', methods=['GET', 'POST'])
@login_required
def delete_ss(id):
    print('remove = ', id)
    form = SaveMailSettingsForm()
    form_googlesheets = spreadsheetForm()
    form_listen = ConfigListenForm()
    ss = Spreadsheets.query.get(id)
    db.session.delete(ss)
    db.session.commit()

    items = db.session.query(MailSettings)
    table = ResultsMailSettings(items)
    table.border = True

    items_ss = db.session.query(Spreadsheets)
    table_ss = ResultsgoodleSS(items_ss)
    table_ss.border = True
    user = User.query.filter_by(id=current_user.id).first()

    return render_template('room.html',
                           title='room',
                           form_mail=form,
                           form_gs=form_googlesheets,
                           form_l=form_listen,
                           table=table,
                           table_ss=table_ss,
                           user=user)


@app.route('/room', methods=['GET', 'POST'])
@login_required
def room():
    user = User.query.filter_by(id=current_user.id).first()
    form = SaveMailSettingsForm()
    form_googlesheets = spreadsheetForm()
    form_listen = ConfigListenForm()
    ss = Spreadsheets.query.filter_by(id_owner=current_user.id).all()
    mails = MailSettings.query.filter_by(id_owner=current_user.id).all()
    #print([item.spreadsheets_id for item in ss])
    form_listen.spreadsheet.choices = [(item.id, item.spreadsheets_id) for item in ss]
    form_listen.mail.choices = [(item.id, item.email) for item in mails]


    items = MailSettings.query.filter_by(id_owner=current_user.id)
    table = ResultsMailSettings(items)
    table.border = True

    items_ss = Spreadsheets.query.filter_by(id_owner=current_user.id)
    table_ss = ResultsgoodleSS(items_ss)
    table_ss.border = True

    return render_template('room.html',
                           title='room',
                           form_mail=form,
                           form_gs=form_googlesheets,
                           form_l=form_listen,
                           table=table,
                           table_ss=table_ss,
                           user=user)


@app.route('/listen', methods=['GET', 'POST'])
@login_required
def listen():
    form_listen = ConfigListenForm()
    if form_listen.is_submitted():
        print('Room validate_on_submit form')
        listen_settings = ListenTask(id_mail=form.server_imap.data,
                                     id_user=User.query.filter_by(id=current_user.id).first(),
                                     id_spreadsheets=form.server_imap.data)
        db.session.add(listen_settings)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('room'))
    return render_template('room.html')


@app.route('/add_mail_settings', methods=['GET', 'POST'])
@login_required
def add_mail_settings():
    form = SaveMailSettingsForm()
    if form.is_submitted():
        print('Room validate_on_submit form')
        mail_settings = MailSettings(id_owner=current_user.id,
                                     server_imap=form.server_imap.data,
                                     server_smpt=form.server_smpt.data,
                                     port=587,
                                     tls=True,
                                     email=form.email.data,
                                     email_default=form.email.data)
        mail_settings.set_mailpassword(form.mail_password.data)
        db.session.add(mail_settings)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('room'))
    return render_template('room.html')


@app.route('/add_google_ss_settings', methods=['GET', 'POST'])
@login_required
def add_google_ss_settings():
    form_googlesheets = spreadsheetForm()
    if form_googlesheets.is_submitted():
        print('Room validate_on_submit form_googlesheets ')
        print(form_googlesheets.spreadsheets_id.data)
        data = json.load(form_googlesheets.credential_file.data)
        ss_settings = Spreadsheets(spreadsheets_id=form_googlesheets.spreadsheets_id.data,
                                   credential_file=data,
                                   id_owner=current_user.id)
        # mail_settings.set_mailpassword(form.mail_password.data)
        db.session.add(ss_settings)
        db.session.commit()
        flash('Congratulations, you are add google sheets!')
        return redirect(url_for('room'))
    return render_template('room.html')


@app.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
    form_listen = ConfigListenForm()
    if form_listen.is_submitted():
        print('Room validate_on_submit form')
        task_listen = ListenTask(id_mail=form_listen.mail.data,
                                 id_owner=current_user.id,
                                 desc=form_listen.desc,
                                 id_spreadsheets=form_listen.spreadsheat.data,
                                 script=form_listen.script.data)
        db.session.add(task_listen)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('room'))
    return render_template('room.html')

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


@app.route('/tabs', methods=['GET', 'POST'])
def tabs():
    return render_template('tabs_example.html')