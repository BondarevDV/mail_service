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
app.config.from_object(Config)
celery = make_celery(app)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

mail = Mail(app)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

login = LoginManager(app)
login.login_view = 'login'
bootstrap = Bootstrap(app)
from app import routes, models

#db.create_all()
#db.drop_all()