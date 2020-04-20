# from flask import Flask
#
# app = Flask(__name__)
#
# from app import routes

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_selery import make_celery
from flask_mail import Mail
import os


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379',
# app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://admin:p4jiaV5M@127.0.0.1:5432/db_googlesheets'
# app.config['SECRET_KEY'] = 'a really really really really long secret key'
# app.config['SQLALCHEMY_MIGRATE_REPO'] = os.path.join(basedir, 'db_repository')
# app.config['MAIL_SERVER'] = 'imap.yandex.ru'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = 'd.bondarev.86@yandex.ru'  # введите свой адрес электронной почты здесь
# app.config['MAIL_DEFAULT_SENDER'] = 'd.bondarev.86@yandex.ru'  # и здесь
# app.config['MAIL_PASSWORD'] = 'kpwoltwjqpsboxde'  # введите пароль
# app.config['SECURITY_EMAIL_SENDER'] = 'd.bondarev.86@yandex.ru'
app.config.from_object(Config)
bootstart = Bootstrap(app)
celery = make_celery(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

mail = Mail(app)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

login = LoginManager(app)
login.login_view = 'login'

from app import routes, models

db.create_all()