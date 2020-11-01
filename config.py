from configparser import ConfigParser
import time


def config(filename='config.ini', section='google_sheets_api'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
    # get section, default to postgresql
    db = {}
    if parser.has_section(section):

        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db


import os
basedir = os.path.abspath(os.path.dirname(__file__))

# class Config(object):
#     # ...
#     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
#         'sqlite:///' + os.path.join(basedir, 'app.db')
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#
#
#
# import os
# basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    CELERY_BROKER_URL = 'redis://localhost:6379',
    CELERY_RESULT_BACKEND = 'redis://localhost:6379'
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://admin:p4jiaV5M@127.0.0.1:5432/db_googlesheets'
    SECRET_KEY = 'a really really really really long secret key'
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

    # SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') # or 'sqlite:///' + os.path.join(basedir, 'app.db')
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_MIGRATE_REPO = os.environ.get('SQLALCHEMY_MIGRATE_REPO')
    # MAIL_SERVER = os.environ.get('MAIL_SERVER')
    # MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    # MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # SECURITY_EMAIL_SENDER = os.environ.get('SECURITY_EMAIL_SENDER')
    # MAIL_SERVER = 'smtp.yandex.ru'
    # MAIL_PORT = 587
    # MAIL_USE_TLS = True
    # MAIL_USERNAME = 'd.bondarev.86@yandex.ru'  # введите свой адрес электронной почты здесь
    # MAIL_DEFAULT_SENDER = 'd.bondarev.86@yandex.ru'  # и здесь
    # MAIL_PASSWORD = 'kpwoltwjqpsboxde'  # введите пароль
    # SECURITY_EMAIL_SENDER = 'd.bondarev.86@yandex.ru'
    #
    # print(MAIL_SERVER)
    # print(MAIL_PORT)
    # print(MAIL_USE_TLS)
    # print(MAIL_USERNAME)
    # print(MAIL_DEFAULT_SENDER)
    # print(MAIL_PASSWORD)
    # print(SECURITY_EMAIL_SENDER)
    # print(SQLALCHEMY_DATABASE_URI)


    # ADMINS = ['your-email@example.com']
    # POSTS_PER_PAGE = 25


def main():
    return config()


if __name__ == "__main__":
    main()