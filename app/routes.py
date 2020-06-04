# -*- coding: utf-8 -*-
from dominate.tags import form
from sqlalchemy import update
from app import app
from app import db
from app import mail
from app.forms import LoginForm
from app.forms import MessageForm
from app.forms import NameForm
from app.forms import RegistrationForm, LoadForm, SaveMailSettingsForm, spreadsheetForm, ConfigListenForm
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, EMailSettings, ResultsEMailSettings, Spreadsheets, ResultsgoodleSS, ListenTask, ResultsTask
from werkzeug.utils import secure_filename
from app.looker import get_list_dir, init_looker_multythread, init_looker
from flask_selery import logger
import logger as MYLOG
import json

import os
from flask_mail import Message
import service_mail
from flask import abort
from flask import redirect
from config import config
from app import celery
from celery.result import AsyncResult
from sqlalchemy import event

LOG_ROUTES = MYLOG.init("ROUTES.log")

# @app.route('/')
# @app.route('/index')
# def index():
#     return render_template('base_bootstrap.html', title='Home')


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/base_bootstrap')
def base_bootstrap():
    return render_template('base_bootstrap.html', title='Home')


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
    mail = EMailSettings.query.get(id)
    db.session.delete(mail)
    db.session.commit()
    return redirect(url_for('room'))


@app.route('/delete_ss/<id>', methods=['GET', 'POST'])
@login_required
def delete_ss(id):
    ss = Spreadsheets.query.get(id)
    db.session.delete(ss)
    db.session.commit()
    return redirect(url_for('room'))


@app.route('/delete_task/<id>', methods=['GET', 'POST'])
@login_required
def delete_task(id):
    task = ListenTask.query.get(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('room'))


@app.route('/folders/<email_id>', methods=['GET', 'POST'])
@login_required
def folders(email_id):
    print('email_id = ', email_id)
    email_settings = EMailSettings.query.filter_by(id_owner=current_user.id).filter_by(id=email_id).first()
    print(email_settings.server_imap)
    print(email_settings.key_access_email)
    print(email_settings.email)
    folders = get_list_dir(imap_host=email_settings.server_imap,
                           login=email_settings.email,
                           password=email_settings.key_access_email)
    if folders is not None:
        list_obj_folders = list()
        i = 0
        for item in folders:
            list_obj_folders.append({'id': i, 'name': item})
            i += 1
        return jsonify({'folders': list_obj_folders})
    else:
        return jsonify({'folders': [{'id': 0, 'name': 'ERROR ACCESS'}, ]})


@app.route('/room', methods=['GET', 'POST'])
@login_required
def room():
    user = User.query.filter_by(id=current_user.id).first()
    form = SaveMailSettingsForm()
    form_googlesheets = spreadsheetForm()
    form_listen = ConfigListenForm()
    ss = Spreadsheets.query.filter_by(id_owner=current_user.id).all()
    emails = EMailSettings.query.filter_by(id_owner=current_user.id).all()

    form_listen.spreadsheet.choices = [(item.id, item.spreadsheets_id) for item in ss]
    form_listen.email.choices = [(item.id, item.email) for item in emails]
    items = EMailSettings.query.filter_by(id_owner=current_user.id)
    table = ResultsEMailSettings(items)
    table.border = True

    items_ss = Spreadsheets.query.filter_by(id_owner=current_user.id)
    table_ss = ResultsgoodleSS(items_ss)
    table_ss.border = True

    items_tasks = ListenTask.query.join(EMailSettings, (ListenTask.id_email == EMailSettings.id))\
        .join(Spreadsheets, (ListenTask.id_spreadsheets == Spreadsheets.id)) \
        .add_columns(ListenTask.id) \
        .add_columns(ListenTask.desc) \
        .add_columns(ListenTask.status) \
        .add_columns(ListenTask.datetime) \
        .add_columns(Spreadsheets.spreadsheets_id)\
        .add_columns(EMailSettings.email)\
        .filter_by(id_owner=current_user.id).order_by(ListenTask.id)
    table_tasks = ResultsTask(items_tasks)
    table_tasks.border = True

    return render_template('room.html',
                           title='room',
                           form_mail=form,
                           form_gs=form_googlesheets,
                           form_l=form_listen,
                           table=table,
                           table_ss=table_ss,
                           table_tasks=table_tasks,
                           user=user)


@app.route('/add_mail_settings', methods=['GET', 'POST'])
@login_required
def add_mail_settings():
    form = SaveMailSettingsForm()
    if form.is_submitted():
        print('Room validate_on_submit form')
        email_settings = EMailSettings(id_owner=current_user.id,
                                       server_imap=form.server_imap.data,
                                       server_smpt=form.server_smpt.data,
                                       port=587,
                                       tls=True,
                                       email=form.email.data,
                                       email_default=form.email.data,
                                       key_access_email=form.key_access_email.data)
        db.session.add(email_settings)
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


@event.listens_for(ListenTask, 'after_insert')
def event_after_insert(mapper, connection, target):
    # Здесь будет очень важная бизнес логика
    print('event_after_insert: ', current_user)
    print('target: ', target.id)


@event.listens_for(ListenTask, 'after_update')
def event_after_update(mapper, connection, target):
    # Здесь будет очень важная бизнес логика
    print('receive_after_update : ', current_user)
    print('target: ', target.id)


@app.route('/update_task_status/<id>', methods=['GET', 'POST'])
@login_required
def update_task_status(id):
    task_status = ListenTask.query.get(id).status
    ListenTask.query.filter_by(id=id).update({'status': (not task_status)})
    db.session.commit()
    return redirect(url_for('room'))


@app.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
    form_listen = ConfigListenForm()
    if form_listen.is_submitted():
        print('Room validate_on_submit form')
        print(form_listen.folder.data)
        script = form_listen.script.data
        task_listen = ListenTask(id_email=int(form_listen.email.data),
                                 id_owner=int(current_user.id),
                                 name=form_listen.name.data,
                                 folder=form_listen.folder.data,
                                 desc=form_listen.desc.data,
                                 id_spreadsheets=int(form_listen.spreadsheet.data))
        db.session.add(task_listen)
        db.session.commit()
        flash('Congratulations, you are add task!')
        return redirect(url_for('room'))
    return render_template('room.html')


@app.route('/start_task/<id>', methods=['GET', 'POST'])
@login_required
def start_task(id):
    task = ListenTask.query.join(EMailSettings, (ListenTask.id_email == EMailSettings.id))\
        .join(Spreadsheets, (ListenTask.id_spreadsheets == Spreadsheets.id)) \
        .add_columns(ListenTask.id) \
        .add_columns(ListenTask.folder)\
        .add_columns(Spreadsheets.spreadsheets_id) \
        .add_columns(Spreadsheets.credential_file) \
        .add_columns(EMailSettings.email) \
        .add_columns(EMailSettings.server_imap) \
        .add_columns(EMailSettings.key_access_email) \
        .filter_by(id_owner=current_user.id).filter_by(id=id).first()

    init_looker_multythread(spreadsheetId=task.spreadsheets_id,
                            google_sheets_creadential_json=task.credential_file,
                            imap_server=task.server_imap,
                            email=task.email,
                            passwd=task.key_access_email,
                            folder=task.folder)
    return redirect(url_for('room'))


def start_task(id):
    task = ListenTask.query.join(EMailSettings, (ListenTask.id_email == EMailSettings.id))\
        .join(Spreadsheets, (ListenTask.id_spreadsheets == Spreadsheets.id)) \
        .add_columns(ListenTask.id) \
        .add_columns(ListenTask.folder)\
        .add_columns(Spreadsheets.spreadsheets_id) \
        .add_columns(Spreadsheets.credential_file) \
        .add_columns(EMailSettings.email) \
        .add_columns(EMailSettings.server_imap) \
        .add_columns(EMailSettings.key_access_email) \
        .filter_by(id=id).first()
    #print(" id = %s" % task.id)
    logger.info(" id = %s" % task.id)
    logger.info(" folder = %s" % task.folder)
    logger.info(" spreadsheets_id = %s" % task.spreadsheets_id)
    # logger.info(" credential_file = %s" % task.credential_file)
    logger.info(" email = %s" % task.email)
    logger.info(" folder = %s" % task.folder)
    init_looker_multythread(spreadsheetId=task.spreadsheets_id,
                            google_sheets_creadential_json=task.credential_file,
                            imap_server=task.server_imap,
                            email=task.email,
                            passwd=task.key_access_email,
                            folder=task.folder)

# @app.route('/send_mail/', methods=['GET', 'POST'])
# def send_mail():
#     # ...
#     # db.session.commit()
#     email = "d.bondarev.86@yandex.ru"
#     name = "Dmitry"
#     msg = Message("Feedback", recipients=[app.config['MAIL_USERNAME']])
#     msg.body = "You have received a new feedback from {} <{}>.".format(name, email)
#     mail.connect()
#     mail.send(msg)
#
#     print("\nData received. Now redirecting ...")
#     return redirect(url_for('index'))


@celery.task
def complete_task(task_id):
    task_inf = "task id = " + str(task_id)
    logger.info(task_inf)
    start_task(task_id)


@celery.task(name="periodic_task")
def periodic_task():
    """periodic_task проверяет таблицу с задачами и тайммерами и создаёт задачу"""
    tasks = ListenTask.query.all()
    logger.info("Start periodic_task")
    for task in tasks:
        print(task.status)
    for task in tasks:
        if task.status:
            complete_task.delay(task.id)

