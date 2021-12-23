import gspread

from Utils.redisUtils import getRedisClient

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'key.json'

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '***REMOVED***'


def main():
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)

    # Call the Sheets API
    spreadsheet = gc.open_by_key(SAMPLE_SPREADSHEET_ID)
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


if __name__ == '__main__':
    main()
