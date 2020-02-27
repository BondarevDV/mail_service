import service_mail
from threading import Thread


class CMail():
    def __init__(self, state):
        self.state = state


    def listen(self):
        while self.state:
            # print('run')
            params = service_mail.config()
            # print(params)
            spreadsheetId = params.get('spreadsheetid', None)
            GOOGLE_CREDENTIALS_FILE = params.get('credential_file', None)
            if spreadsheetId is not None:
                service_mail.main(spreadsheetId, GOOGLE_CREDENTIALS_FILE)
        self.thread.join()

    def set_state(self, state: True):
        self.state = state


    def Run(self):
        self.thread = Thread(target=self.listen, args=())
        self.thread.start()


def main():
    mail_obj = CMail(True)
    mail_obj.Run()


if __name__ == '__main__':
    main()
