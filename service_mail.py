# -*- coding: utf-8 -*-

import imaplib
import getpass
import email
import base64
import re
from datetime import datetime
import google_sheets


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
        print('address Not found')
        return


def get_driver(text):
    template = r"Контакты водителя:.*С Уважением"
    match = re.search(template, text, re.DOTALL)
    if match:
        driver = get_substring(match[0], "Контакты водителя:", "С Уважением")
        return driver
    else:
        print('address Not found')
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
        print('address Not found')
        return


def get_cement_grade(text):
    template = r"цемент.*марки.*''.*''"
    match = re.search(template, text)
    if match:
        cement_grade = del_quote(match[0], r"''")
        return cement_grade
    else:
        print('address Not found')
        return


def get_cement_weight(text):
    template = r"весом \d*.\d*.*"
    match = re.search(template, text)
    if match:
        cement_weight = get_substring(match[0], "весом", "тонн.")
        return float(cement_weight.replace(',', '.'))
    else:
        print('address Not found')
        return


def read_yandexru(name_folder):
    mail = imaplib.IMAP4_SSL('imap.yandex.ru')
    mail.login('d.bondarev.86@yandex.ru', 'kpwoltwjqpsboxde')
    mail.list()

    # Выводит список папок в почтовом ящике.
    #mail.select("inbox")  # Подключаемся к папке "входящие".
    #mail.create("test")  # Подключаемся к папке "входящие".
    mail.select(name_folder.encode("utf-8"))
    #print(mail.search(None, 'ALL'))

    result, data = mail.uid('search', None, "ALL")  # Выполняет поиск и возвращает UID писем.
    latest_email_uid = data[0].split()[-1]
    result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
    raw_email = data[0][1]
    email_message = email.message_from_bytes(raw_email)
    #print('SUBJECT')
    date_text = base64.b64decode(email_message['SUBJECT'].replace('?UTF-8?B?', '')).decode("utf-8", "replace")
    #print(base64.b64decode(get_first_text_block(email_message['SUBJECT'])).decode("utf-8", "replace"))
    #print('TO')
    #print(email_message['To'])

    #print(email.utils.parseaddr(email_message['From']))  # получаем имя отправителя "Yuji Tomita"

    # for item in email_message.items():
    #     print(item)  # Выводит все заголовки.
    # print(email_message['Subject'])
    data = base64.b64decode(get_first_text_block(email_message)).decode("utf-8", "replace")
    data_dict = dict()
    data_dict['cement_grade'] = get_cement_grade(data)
    data_dict['driver'] = get_driver(data)
    data_dict['address'] = get_address(data)
    data_dict['date_shipment'] = get_date_shipment(date_text)
    data_dict['cement_weight'] = get_cement_weight(data)
    print(data_dict)

    #print(data)


### lagvftfalqbxsapx
def read_mailru(name_folder):
    mail = imaplib.IMAP4_SSL('imap.mail.ru')
    mail.login('d.bondarev.86@mail.ru', 'gmgvaivcapzcatky')
    mail.list()

    # Выводит список папок в почтовом ящике.
    #mail.select("inbox")  # Подключаемся к папке "входящие".
    #mail.create("test")  # Подключаемся к папке "входящие".
    mail.select(name_folder.encode("utf-8"))
    print(mail.search(None, 'ALL'))

    result, data = mail.uid('search', None, "ALL")  # Выполняет поиск и возвращает UID писем.
    latest_email_uid = data[0].split()[-1]
    result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
    raw_email = data[0][1]
    email_message = email.message_from_bytes(raw_email)


    print(email_message['To'])

    print(email.utils.parseaddr(email_message['From']))  # получаем имя отправителя "Yuji Tomita"

    # for item in email_message.items():
    #     print(item)  # Выводит все заголовки.
    # print(email_message['Subject'])
    print(base64.b64decode(get_first_text_block(email_message)).decode("utf-8", "replace"))



def read_gmail():
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login('d.bondarev.86@gmail.com', 'lagvftfalqbxsapx')
    mail.list()

    # Выводит список папок в почтовом ящике.
    #mail.select("inbox")  # Подключаемся к папке "входящие".
    #mail.create("test")  # Подключаемся к папке "входящие".
    mail.select("test")
    print(mail.search(None, 'ALL'))

    result, data = mail.uid('search', None, "ALL")  # Выполняет поиск и возвращает UID писем.
    latest_email_uid = data[0].split()[-1]
    result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
    raw_email = data[0][1]
    email_message = email.message_from_bytes(raw_email)

    print(email_message['To'])

    print(email.utils.parseaddr(email_message['From']))  # получаем имя отправителя "Yuji Tomita"

    # for item in email_message.items():
    #     print(item)  # Выводит все заголовки.
    # print(email_message['Subject'])
    print(base64.b64decode(get_first_text_block(email_message)).decode("utf-8"))


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


def create_spread_sheat(docTitle="title", sheetTitle="test_table"):
    ss = google_sheets.Spreadsheet(google_sheets.GOOGLE_CREDENTIALS_FILE, debugMode=True)
    rowCount = 1
    ss.create(docTitle, sheetTitle, rows=rowCount, cols=6, locale="ru_RU", timeZone="Europe/Moscow")
    return ss.getSheetURL()


def append_rowdata(spreadsheetId, service, values):
    set_cellformat(spreadsheetId)
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


def set_cellformat(spreadsheetId):
    ss = google_sheets.Spreadsheet(google_sheets.GOOGLE_CREDENTIALS_FILE, debugMode=True)
    ss.setSpreadsheetById(spreadsheetId)
    # ss.sheetId = 0
    print(ss.get_spreadsheet_gridProperties(0))
    rowindex = ss.get_spreadsheet_gridProperties(0)['rowCount']
    ss.prepare_setCellsFormat("A{0}:A{0}".format(rowindex), {"numberFormat": {"type": "DATE", "pattern": "dd.mm.yyyy"}, "horizontalAlignment": "CENTER"})
    ss.prepare_setCellsFormat("B{0}:B{0}".format(rowindex), {"numberFormat": {"type": "NUMBER", "pattern": "#,##0.00"},
                                        "horizontalAlignment": "CENTER"})
    ss.prepare_setCellsFormat("C{0}:C{0}".format(rowindex), {"textFormat": {"bold": True}, "horizontalAlignment": "CENTER"})
    ss.prepare_setCellsFormat("D{0}:D{0}".format(rowindex), {"textFormat": {"bold": True}, "horizontalAlignment": "CENTER"})
    ss.prepare_setCellsFormat("E{0}:E{0}".format(rowindex), {"textFormat": {"bold": True}, "horizontalAlignment": "CENTER"})
    ss.runPrepared()
    return ss.service



def open_spread_sheat(spreadsheetId):
    ss = google_sheets.Spreadsheet(google_sheets.GOOGLE_CREDENTIALS_FILE, debugMode=True)
    ss.setSpreadsheetById(spreadsheetId)
    return ss.service


def create_spread_sheat():
    ss = google_sheets.Spreadsheet(google_sheets.GOOGLE_CREDENTIALS_FILE, debugMode=True)
    docTitle = "title"
    sheetTitle = "test_table"
    rowCount = 1
    ss.create(docTitle, sheetTitle, rows=rowCount, cols=6, locale="ru_RU", timeZone="Europe/Moscow")
    ss.shareWithAnybodyForWriting()
    print(ss.getSheetURL())


if __name__ == "__main__":
    spreadsheetId = '1Kfkwystan1K4j_K712OysWXeqzBscwCm2bEOahYCLXw'
    # service = set_cellformat(spreadsheetId)

    service = open_spread_sheat(spreadsheetId)
    append_rowdata(spreadsheetId, service, ["07.09.2019", "35,26", "Портландцемент ЦЕМ I 32,5Б", "Вася 916...", "Москва", "6"])
    set_cellformat(spreadsheetId)
    # create_spread_sheat()
    # read_yandexru("test2")
    # open_spread_sheat()



