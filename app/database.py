from app.models import User, EMailSettings, ResultsEMailSettings, Spreadsheets, ResultsgoodleSS, ListenTask, ResultsTask,ResultsgoodleSSSingle
from app import db
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import RegistrationForm, LoadForm, SaveMailSettingsForm, spreadsheetForm, ConfigListenForm
from app.forms import LoginForm

class DBMail_service():

    def get_tasks(self):
        form_listen = ConfigListenForm()
        ss = Spreadsheets.query.filter_by(id_owner=current_user.id).all()
        emails = EMailSettings.query.filter_by(id_owner=current_user.id).all()
        form_listen.spreadsheet.choices = [(item.id, item.spreadsheets_id) for item in ss]
        form_listen.email.choices = [(item.id, item.email) for item in emails]
        return form_listen

    def get_google_ss(self):
        form_googlesheets = spreadsheetForm()
        items_ss = Spreadsheets.query.filter_by(id_owner=current_user.id)
        table_ss = ResultsgoodleSSSingle(items_ss)
        table_ss.border = True
        return form_googlesheets, table_ss

    def get_mails(self):
        form = SaveMailSettingsForm()
        return form



