# -*- coding: utf-8 -*-

import imaplib
import getpass
import email
import base64
import re
from datetime import datetime
import google_sheets
from multiprocessing import Pool
from multiprocessing import Process, Queue
from config import config
import logger
import time
import ssl
import shlex
import json
import os
import threading
import urllib.request
from queue import Queue

from google_sheets import GOOGLE_CREDENTIALS_FILE

LOG = logger.init("INFO.log")


def del_quote(text, quote_str):
    return text[text.find(quote_str) + len(quote_str): text.rfind(quote_str)]


def get_substring(text, lstr, rstr):
    return text[text.find(lstr) + len(lstr): text.rfind(rstr)]


def get_address(text):
    template = r"по адресу:.*''.*''"
    match = re.search(template, text)
    if match:
        address = del_quote(match[0], r"''")
        return address
    else:
        LOG.warning('Адресс Not found')
        # print('address Not found')
        return


def get_driver(text):
    template = r"Контакты водителя:.*С Уважением"
    match = re.search(template, text, re.DOTALL)
    if match:
        driver = get_substring(match[0], "Контакты водителя:", "С Уважением")
        return driver
    else:
        # print('address Not found')
        LOG.warning('Контакты водителя Not found')
        return


def get_date_shipment(text):
    template = r"на.*"
    match = re.search(template, text)
    # print( ' date = ', match[0] if match else 'Not found')
    if match:
        date_shipment = match[0].split(' ')
        datetime_object = datetime.strptime(date_shipment[1], '%d.%m.%Y')
        return date_shipment[1]
    else:
        # print('address Not found')
        LOG.warning('Дата поступления Not found')
        return


def get_cement_grade(text):
    template = r"цемент.*марки.*''.*''"
    match = re.search(template, text)
    if match:
        cement_grade = del_quote(match[0], r"''")
        return cement_grade
    else:
        # print('address Not found')
        LOG.warning('Марка цемента Not found')
        return


def get_cement_weight(text):
    template = r"весом \d*.\d*.*"
    match = re.search(template, text)
    if match:
        cement_weight = get_substring(match[0], "весом", "тонн.")
        return float(cement_weight.replace(',', '.'))
    else:
        # print('address Not found')
        LOG.warning('Cement weight (Вес цемента) Not found')
        return


def read_yandexru(name_folder):
    #try:
    mail = imaplib.IMAP4_SSL('imap.yandex.ru')
    mail.login('d.bondarev.86@yandex.ru', 'kpwoltwjqpsboxde')
    mail.list()
    mail.select(name_folder.encode("utf-8"))
    result, data = mail.uid('search', None, "UNSEEN")  # Выполняет поиск и возвращает UID писем.
    email_uids = data[0].split()
    if len(email_uids) == 0:
        yield None
    else:
        # print('length = ', len(email_uids))
        LOG.info('length = {}'.format(len(email_uids)))
        for uid in email_uids:
            result, data = mail.uid('fetch', uid, '(RFC822)')
            raw_email = data[0][1]
            num = 0
            while type(raw_email) is int:
                num += 1
                raw_email = data[num][1]
                print("lala")
            # print(" data[0][1] =", data)
            # print(" raw_email =", raw_email)
            # print(" result =", result)
            LOG.error(raw_email)
            email_message = email.message_from_bytes(raw_email)
            date_text = base64.b64decode(email_message['SUBJECT'].replace('?UTF-8?B?', '')).decode("utf-8", "replace")
            data = base64.b64decode(get_first_text_block(email_message)).decode("utf-8", "replace")
            data_dict = dict()
            data_dict['cement_grade'] = get_cement_grade(data)
            data_dict['driver'] = get_driver(data)
            data_dict['address'] = get_address(data)
            data_dict['date_shipment'] = get_date_shipment(date_text)
            data_dict['cement_weight'] = get_cement_weight(data)

            yield data_dict
            #     print(data_dict)
            #     list_mail_info.append(data_dict)
            # return list_mail_info
    # except Exception as ex:
    #     print(ex)
    #     LOG.error(ex)
    #     yield None



### lagvftfalqbxsapx
def read_mailru(name_folder):
    mail = imaplib.IMAP4_SSL('imap.mail.ru')
    mail.login('d.bondarev.86@mail.ru', 'gmgvaivcapzcatky')
    mail.list()

    # Выводит список папок в почтовом ящике.
    #mail.select("inbox")  # Подключаемся к папке "входящие".
    #mail.create("test")  # Подключаемся к папке "входящие".
    mail.select(name_folder.encode("utf-8"))
    # print(mail.search(None, 'ALL'))
    LOG.info(mail.search(None, 'ALL'))

    result, data = mail.uid('search', None, "ALL")  # Выполняет поиск и возвращает UID писем.
    latest_email_uid = data[0].split()[-1]
    result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
    raw_email = data[0][1]
    email_message = email.message_from_bytes(raw_email)

    LOG.info(email_message['To'])
    LOG.info(email.utils.parseaddr(email_message['From']))
    LOG.info(base64.b64decode(get_first_text_block(email_message)).decode("utf-8", "replace"))
    # print(email_message['To'])

    # print(email.utils.parseaddr(email_message['From']))  # получаем имя отправителя "Yuji Tomita"

    # for item in email_message.items():
    #     print(item)  # Выводит все заголовки.
    # print(email_message['Subject'])
    # print(base64.b64decode(get_first_text_block(email_message)).decode("utf-8", "replace"))



def read_gmail():
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login('d.bondarev.86@gmail.com', 'lagvftfalqbxsapx')
    mail.list()

    # Выводит список папок в почтовом ящике.
    #mail.select("inbox")  # Подключаемся к папке "входящие".
    #mail.create("test")  # Подключаемся к папке "входящие".
    mail.select("test")
    LOG.info(mail.search(None, 'ALL'))

    result, data = mail.uid('search', None, "ALL")  # Выполняет поиск и возвращает UID писем.
    latest_email_uid = data[0].split()[-1]
    result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
    raw_email = data[0][1]
    email_message = email.message_from_bytes(raw_email)

    LOG.info(email_message['To'])

    LOG.info(email.utils.parseaddr(email_message['From']))  # получаем имя отправителя "Yuji Tomita"

    # for item in email_message.items():
    #     print(item)  # Выводит все заголовки.
    # print(email_message['Subject'])
    LOG.info(base64.b64decode(get_first_text_block(email_message)).decode("utf-8"))


# gmgvaivcapzcatky

def get_first_text_block(email_message_instance):
    """
    :param email_message_instance:
    :return:
    """
    maintype = email_message_instance.get_content_maintype()
    if maintype == 'multipart':
        for part in email_message_instance.get_payload():
            if part.get_content_maintype() == 'text':
                return part.get_payload()
    elif maintype == 'text':
        return email_message_instance.get_payload()


def create_ss(docTitle="title", sheetTitle="test_table", google_sheets_creadential_json=GOOGLE_CREDENTIALS_FILE):
    ss = google_sheets.SpreadsheetJSONData(google_sheets_creadential_json, debugMode=True)
    rowCount = 1
    ss.create(docTitle, sheetTitle, rows=rowCount, cols=6, locale="ru_RU", timeZone="Europe/Moscow")
    return ss.getSheetURL()


def append_rowdata(spreadsheetId, service, values, google_sheets_creadential_json):
    set_cellformat(spreadsheetId, google_sheets_creadential_json)
    list = [values]
    resource = {
        "majorDimension": "ROWS",
        "values": list,
        "range": "A1:F1"
    }
    spreadsheetId = spreadsheetId
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheetId,
        range='A1:F1',
        body=resource,
        valueInputOption="USER_ENTERED"
    ).execute()


grid = {
    1: 'A',
    2: 'B',
    3: 'C',
    4: 'D',
    5: 'E',
    6: 'F',
}


def set_cellformat(spreadsheetId, google_sheets_creadential_json):
    ss = google_sheets.SpreadsheetJSONData(google_sheets_creadential_json, debugMode=True)
    ss.setSpreadsheetById(spreadsheetId)
    # ss.sheetId = 0
    # print(ss.get_spreadsheet_gridProperties(0))
    LOG.info(ss.get_spreadsheet_gridProperties(0))
    rowindex = ss.get_spreadsheet_gridProperties(0)['rowCount']
    ss.prepare_setCellsFormat("A{0}:A{0}".format(rowindex), {"numberFormat": {"type": "DATE", "pattern": "dd.mm.yyyy"}, "horizontalAlignment": "CENTER"})
    ss.prepare_setCellsFormat("B{0}:B{0}".format(rowindex), {"numberFormat": {"type": "NUMBER", "pattern": "#,##0.00"},
                                        "horizontalAlignment": "CENTER"})
    ss.prepare_setCellsFormat("C{0}:C{0}".format(rowindex), {"textFormat": {"bold": True}, "horizontalAlignment": "CENTER"})
    ss.prepare_setCellsFormat("D{0}:D{0}".format(rowindex), {"textFormat": {"bold": True}, "horizontalAlignment": "CENTER"})
    ss.prepare_setCellsFormat("E{0}:E{0}".format(rowindex), {"textFormat": {"bold": True}, "horizontalAlignment": "CENTER"})
    ss.runPrepared()
    return ss.service


def open_ss(spreadsheetId, google_sheets_creadential_json):
    ss = google_sheets.SpreadsheetJSONData(google_sheets_creadential_json, debugMode=True)
    ss.setSpreadsheetById(spreadsheetId)
    return ss.service


def create_ss(google_sheets_creadential_json):
    ss = google_sheets.SpreadsheetJSONData(google_sheets_creadential_json, debugMode=True)
    docTitle = "title"
    sheetTitle = "test_table"
    rowCount = 1
    ss.create(docTitle, sheetTitle, rows=rowCount, cols=5, locale="ru_RU", timeZone="Europe/Moscow")
    ss.shareWithAnybodyForWriting()
    print(ss.getSheetURL())
    LOG.info(ss.getSheetURL())


# def main():
#     try:
#         nCPU = mp.cpu_count()
#         nJobs = nCPU * 36
#         print(nCPU)
#         data = sql_updater.get_data_fromtable(templates.get_streams)
#         print(len(data))
#         p = Pool(nJobs)
#         p.map(ffprobe_url, data)
#         tools.save_to_json("GET_TREK.json", data)
#     except Exception as e:
#         p.close()
#         p.terminate()


def main(spreadsheetId, google_sheets_creadential_json):
    mails_info = read_yandexru("test2")
    for mail in mails_info:
        if mail is not None:
            data = list()
            data.append(mail['date_shipment'])
            data.append(mail['cement_weight'])
            data.append(mail['cement_grade'])
            data.append(mail['driver'])
            data.append(mail['address'])
            service = open_ss(spreadsheetId, google_sheets_creadential_json)
            append_rowdata(spreadsheetId, service, data, google_sheets_creadential_json)
            set_cellformat(spreadsheetId, google_sheets_creadential_json)
        else:
            print("Mail is not found")
            # LOG.info("Mail is not found")


def get_data_email_message(name_folder, IMAP4_server):
    IMAP4_server.list()
    IMAP4_server.select(name_folder.encode("utf-8"))
    result, data = IMAP4_server.uid('search', None, "UNSEEN")  # Выполняет поиск и возвращает UID писем.
    email_uids = data[0].split()
    if len(email_uids) == 0:
        yield None
    else:
        LOG.info('length = {}'.format(len(email_uids)))
        for uid in email_uids:
            result, data = IMAP4_server.uid('fetch', uid, '(RFC822)')
            raw_email = data[0][1]
            num = 0
            while type(raw_email) is int:
                num += 1
                raw_email = data[num][1]
                print("lala")
            LOG.error(raw_email)
            email_message = email.message_from_bytes(raw_email)
            date_text = base64.b64decode(email_message['SUBJECT'].replace('?UTF-8?B?', '')).decode("utf-8", "replace")
            data = base64.b64decode(get_first_text_block(email_message)).decode("utf-8", "replace")
            data_dict = dict()
            data_dict['cement_grade'] = get_cement_grade(data)
            data_dict['driver'] = get_driver(data)
            data_dict['address'] = get_address(data)
            data_dict['date_shipment'] = get_date_shipment(date_text)
            data_dict['cement_weight'] = get_cement_weight(data)
            yield data_dict


def init_looker(spreadsheetId, google_sheets_creadential_json, imap_server, email, passwd, folder):
    IMAP4_server = imaplib.IMAP4_SSL(imap_server)
    IMAP4_server.login(email, passwd)
    mails_info = get_data_email_message(folder, IMAP4_server)
    for mail in mails_info:
        if mail is not None:
            data = list()
            data.append(mail['date_shipment'])
            data.append(mail['cement_weight'])
            data.append(mail['cement_grade'])
            data.append(mail['driver'])
            data.append(mail['address'])
            service = open_ss(spreadsheetId, google_sheets_creadential_json)
            append_rowdata(spreadsheetId, service, data, google_sheets_creadential_json)
            set_cellformat(spreadsheetId, google_sheets_creadential_json)
        else:
            print("Mail is not found")


def init_looker_multythread(spreadsheetId, google_sheets_creadential_json, imap_server, email, passwd, folder):
    IMAP4_server = imaplib.IMAP4_SSL(imap_server)
    IMAP4_server.login(email, passwd)
    emails_info = get_data_email_message(folder, IMAP4_server)
    """
    Запускаем программу
    """
    queue = Queue()

    # Запускаем очередь
    for i in range(5):
        t = SSWriter(queue, spreadsheetId, google_sheets_creadential_json)
        t.setDaemon(True)
        t.start()

    # Добавляем в очередь письмо
    for email in emails_info:
        queue.put(email)

    # Ждем завершения работы очереди
    queue.join()


def b64padanddecode(b):
    """Decode unpadded base64 data"""
    b += (-len(b)%4) * '='  # base64 padding (if adds '===', no valid padding anyway)
    return base64.b64decode(b, altchars='+,', validate=True).decode('utf-16-be')


def imaputf7decode(s):
    """Decode a string encoded according to RFC2060 aka IMAP UTF7.

Minimal validation of input, only works with trusted data"""
    lst = s.split('&')
    out = lst[0]
    for e in lst[1:]:
        u, a = e.split('-', 1) #u: utf16 between & and 1st -, a: ASCII chars folowing it
        if u == '':
            out += '&'
        else:
            out += b64padanddecode(u)
        out += a
    return out


def get_list_dir(imap_host, login, password):
    try:
        with imaplib.IMAP4_SSL(imap_host, ssl_context=ssl.create_default_context()) as mail:
            mail.login(login, password)
            list_folders = list()
            for folder in mail.list()[1]:
                fldr = shlex.split(imaputf7decode(folder.decode()))[-1]
                list_folders.append(fldr)
            return list_folders
    except Exception as ex:
        return None


def get_obj_json_from_file(filename):
    with open(filename, 'r') as file_obj:
        client_credentials = json.load(file_obj)
    return client_credentials


class SilentLooker(threading.Thread):
    """Google SS writer"""

    def __init__(self, queue, folder, IMAP4_server):
        """Инициализация потока"""
        threading.Thread.__init__(self)
        self.queue = queue
        self.IMAP4_server = IMAP4_server
        self.folder = folder
        self.status = True
        self.setDaemon(True)

    def run(self):
        """Запуск потока"""
        print('Запуск потока')
        while self.status:
            emails_info = get_data_email_message(self.folder, self.IMAP4_server)
            for email in emails_info:
                self.queue.put(email)

    def stop(self, status):
        self.status = status
        self.join()


class SSWriter(threading.Thread):
    """Google SS writer"""

    def __init__(self, queue, spreadsheetId, google_sheets_creadential_json):
        """Инициализация потока"""
        threading.Thread.__init__(self)
        self.queue = queue
        self.spreadsheetId = spreadsheetId
        self.google_sheets_creadential_json = google_sheets_creadential_json
        self.service = open_ss(self.spreadsheetId, self.google_sheets_creadential_json)

    def run(self):
        """Запуск потока"""
        while True:
            # Получаем url из очереди
            email = self.queue.get()

            # Скачиваем файл
            self.read(email)

            # Отправляем сигнал о том, что задача завершена
            self.queue.task_done()

    def read(self, email):
        if email is not None:
            data = list()
            data.append(email.get('date_shipment', 'None'))
            data.append(email.get('cement_weight', 'None'))
            data.append(email.get('cement_grade', 'None'))
            data.append(email.get('driver', 'None'))
            data.append(email.get('address', 'None'))
            append_rowdata(self.spreadsheetId, self.service, data, self.google_sheets_creadential_json)
            set_cellformat(self.spreadsheetId, self.google_sheets_creadential_json)
        else:
            print("Mail is not found")


def test_looker():
    print('Прослушивание почты...')
    params = config()
    spreadsheetId = params.get('spreadsheetid', None)
    GOOGLE_CREDENTIALS_FILE = params.get('credential_file', None)

    GOOGLE_CREDENTIALS_DATA = get_obj_json_from_file(GOOGLE_CREDENTIALS_FILE)
    google_sheets_creadential_json = GOOGLE_CREDENTIALS_DATA
    # while True:
    #     init_looker_multythread(spreadsheetId=spreadsheetId,
    #                        google_sheets_creadential_json=GOOGLE_CREDENTIALS_DATA,
    #                        imap_server='imap.yandex.ru',
    #                        email='d.bondarev.86@yandex.ru',
    #                        passwd='kpwoltwjqpsboxde',
    #                        folder='test2')
    imap_server = 'imap.yandex.ru'
    email = 'd.bondarev.86@yandex.ru'
    passwd = 'kpwoltwjqpsboxde'
    folder = 'test2'
    queue = Queue()
    IMAP4_server = imaplib.IMAP4_SSL(imap_server)
    IMAP4_server.login(email, passwd)
    look = SilentLooker(queue, folder, IMAP4_server)


    # Запускаем потом и очередь
    for i in range(5):
        t = SSWriter(queue, spreadsheetId, google_sheets_creadential_json)
        t.setDaemon(True)
        t.start()

    look.run()
    # Ждем завершения работы очереди
    queue.join()


def test_get_listpaths():
    print(get_list_dir(imap_host='imap.yandex.ru', login='d.bondarev.86@yandex.ru', password='kpwoltwjqpsboxde'))


if __name__ == "__main__":
    try:
        #test_get_listpaths()
        test_looker()
    except KeyboardInterrupt:
        print('Скрипт остановлен...')




