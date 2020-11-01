import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
import gspread




def create_service_object():
    CREDENTIALS_FILE = 'BDV-CRM-9eb36b64fb66.json'  # имя файла с закрытым ключом

    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)


    spreadsheet_body = {
        'properties': {'title': 'test_bdv_6', 'locale': 'ru_RU'},
        'sheets': [{'properties': {'sheetType': 'GRID',
                                   'sheetId': 123456,
                                   'title': '1',
                                   'gridProperties': {'rowCount': 8, 'columnCount': 5}}}]
    }

    request = service.spreadsheets().create(body=spreadsheet_body)
    response = request.execute()

    # TODO: Change code below to process the `response` dict:
    print("response = ", response)

    driveService = apiclient.discovery.build('drive', 'v3', http=httpAuth)
    shareRes = driveService.permissions().create(
        fileId=response['spreadsheetId'],
        body={'type': 'user', 'role': 'writer', 'emailAddress': 'd.bondarev.86@gmail.com'},
        # доступ на чтение кому угодно
    ).execute()



def insert_data(data: list, service):
    values = [["Действие", "Категория полезности", "Начато", "Завершено", "Потрачено"]]




def main():
    create_service_object()
    #create_table(service)


if __name__ == "__main__":
    main()
