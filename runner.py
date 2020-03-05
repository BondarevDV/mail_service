from app import app
UPLOAD_FOLDER = './'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS
app.run(debug=True)


# @app.shell_context_processor
# def make_shell_context():
#     return {
#         'db': db,
#         'User': User,
#         'Post': Post,
#         'Message': Message,
#         'Task': Task,
#         'mail_settings': MailSettings,
#         'spreadsheets': Spreadsheets,
#         'listen_task': ListenTask
#     }





