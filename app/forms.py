from flask_wtf import FlaskForm
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, Form, \
    TextField, TextAreaField, validators, SubmitField, FileField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User
from wtforms.validators import Required


class ConfigListenForm(FlaskForm):
    HOUR_CHOICES = [('1', '8am'), ('2', '10am')]
    mail = SelectField('Доступная почта:', choices=HOUR_CHOICES)
    dir = StringField('dir: ', validators=[DataRequired()])
    spreadsheats = SelectField('Доступные таблицы google:', choices=HOUR_CHOICES)
    submit = SubmitField('Добавить')


class SaveMailSettingsForm(FlaskForm):
    server_smpt = StringField('server_smpt: ', validators=[DataRequired()])
    server_imap = StringField('server_imap: ', validators=[DataRequired()])
    email = StringField('email: ', validators=[DataRequired()])
    mail_password = PasswordField('Password', validators=[DataRequired()])
    mail_password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('mail_password')])
    submit = SubmitField('Добавить')


class spreadsheetForm(FlaskForm):
    spreadsheets_id = StringField('spreadsheets_id: ', validators=[DataRequired()])
    credential_file = FileField('credential file: ', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class LoadForm(FlaskForm):
    PathToFile = StringField('Path', validators=[DataRequired()])
    submit = SubmitField('Upload')


class MessageForm(FlaskForm):
    PathToFile = StringField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')
