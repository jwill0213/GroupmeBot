from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'key.json'

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '***REMOVED***'


def main():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheetAPI = service.spreadsheets()
    result = sheetAPI.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                   range="TIME!A1:B30").execute()
    values = result.get('values', [])

    req = sheetAPI.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                   valueInputOption='USER_ENTERED', range='SHIB!A1:B30', body={'values': values}).execute()

    if not values:
        print('No data found.')
    else:
        print('Name, Major:')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print('%s, %s' % (row[0], row[1]))


def addSheet(spreadsheetAPI, sheetID, sheetName):
    try:
        request_body = {
            'requests': [{
                'addSheet': {
                    'properties': {
                        'title': sheetName
                    }
                }
            }]
        }

        response = spreadsheetAPI.batchUpdate(
            spreadsheetId=sheetID,
            body=request_body
        ).execute()

        return response
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
