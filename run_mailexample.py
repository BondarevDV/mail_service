from flask import Flask
from flask_mail import Mail, Message

app =Flask(__name__)
mail=Mail(app)

app.config['MAIL_SERVER'] = 'smtp.yandex.ru'
app.config['MAIL_DEFAULT_SENDER'] = 'd.bondarev.86@yandex.ru'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'd.bondarev.86@yandex.ru'
app.config['MAIL_PASSWORD'] = 'zcrxihvbtziluaka'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


@app.route("/test")
def test():
   # msg = Message('Hello', sender='d.bondarev.86@yandex.ru', recipients=['d.bondarev.86@yandex.ru'])
   # msg.body = "Hello Flask message sent from Flask-Mail"
   # mail.send(msg)
    print('test 1')
    with mail.connect() as conn:
        message = '...'
        subject = "hello"
        msg = Message(recipients=['d.bondarev.86@yandex.ru'],
                body=message,
                subject=subject)

        conn.send(msg)
    print('test 2')
    return "Sent"


if __name__ == '__main__':
   app.run(debug = True)