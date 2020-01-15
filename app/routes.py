# -*- coding: utf-8 -*-
from app import app
from app import db
from app.forms import LoginForm
from app.forms import RegistrationForm, LoadForm
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.utils import secure_filename
import os
import service_mail
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
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

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


@app.route('/start/<cmd>', methods=['GET', 'POST'])
@login_required
def run(cmd):
    if cmd == start:
    while state:
        params = config()
        spreadsheetId = params.get('spreadsheetid', None)
        GOOGLE_CREDENTIALS_FILE = params.get('credential_file', None)
        if spreadsheetId is not None:
            main(spreadsheetId)




