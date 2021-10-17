import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.auth import exceptions

#This class encompasses the knowledge of how to interact with Nubi's
#innovatory spread sheet.
class nubiInventory:
    #Nubi ET inventory Test
#    SPREADSHEET_ID = '1smNVdIyMudt2V321mtnUkkN9J8vD5euAzD0eGn2BO_Y' #Test sheet
    SPREADSHEET_ID = '1TSyyx8RIoGnWmjBRkdPQILtYQzK1mEjLYLbIxEhNidQ' #live sheet
    
    CREDENTIALS_FILE = 'nubibot2000-credentials.json'
    sheet = None
    firstRow = None

    def __init__(self):
        service = self.__serviceSetup()
        # Call the Sheets API
        self.sheet = service.spreadsheets()
        self.firstRow = self.__readRange(f'a1:$1')

    def __serviceSetup(self):
        """Shows basic usage of the Sheets API.
        Prints values from a sample spreadsheet.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        creds = service_account.Credentials.from_service_account_file(
            self.CREDENTIALS_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets'])
        return build('sheets', 'v4', credentials=creds)

    def __readRange(self, range: str):
        result = self.sheet.values().get(spreadsheetId=self.SPREADSHEET_ID,
                                    range=range).execute()
        values = result.get('values', [])

        if not values:
#            print('No data found.')
            return None
        else:
            return values

    def clearCell(self, col: str, row: str):
        cell = f'{col}{row}'
        result = self.sheet.values().clear(
            spreadsheetId=self.SPREADSHEET_ID, range=cell).execute()
        if cell in result.get('clearedRange'):
            print(f"{cell} is now clear.")
        else:
            print(f"Could not clear range '{cell}'; result = {result}")

    def clearCellByName(self, colName: str, row: str):
        colLetter = self.__getColLetterFromName(colName)
        self.clearCell(colLetter, row)

    #cell exmaple 'a1' or 'c12' its the A1 name of the cell
    def writeCell(self, cell: str, data: str):
        body = {'values': [[data]]}
        result = self.sheet.values().update(
            spreadsheetId=self.SPREADSHEET_ID, range=cell,
            valueInputOption="USER_ENTERED", body=body).execute()
        print('{0} cells updated.'.format(result.get('updatedCells')))

    def writeCellByName(self, colName: str, row: str, data: str):
        cell = f'{self.__getColLetterFromName(colName)}{row}'
        self.writeCell(cell, data)

    def __getColLetterFromName(self, name: str):
        colLetter = 'A'
        for colName in self.firstRow[0]:
            if colName == name:
                return colLetter
            colLetter = chr(ord(colLetter) + 1)
        print(f"The column {name} does not exist.")
        return None
        
    def readCell(self, col: str, row: str):
        return self.__readRange(f'{col}{row}')

    def readCellByName(self, colName: str, row: str):
        col = self.__getColLetterFromName(colName)
        return self.readCell(col, row)

    def readColByName(self, name: str):
        col = self.__getColLetterFromName(name)
        if col:
            value = self.__readRange(f'{col}:{col}')
            return value
        return None

    def dump(self):
        values = self.__readRange('a1:q112')

        if not values:
            print('No data found.')
        else:
            for row in values:
                # Print columns A and E, which correspond to indices 0 and 4.
                #print('%s, %s' % (row[0], row[4]))
                print(row)

    def run(self, userName:str, assetId: str):
        #Step 1: Read the column with all the assetIds
        self.dump()
        listOfItems = self.readColByName('Asset ID')

        #Step 2: Find the row for this asset
        row = None
        i = 1
        for x in listOfItems:
            if x and x[0] == assetId:
                row = str(i)
                print(f"found {assetId} in row {row}")
                break
            i += 1
        if not row:
            print(f"Could not find [{assetId}]")
            return f"Could not find [{assetId}]"

        #Step 3: Check to see if this asset is already checked out
        checkedOutTo = self.readCellByName('Checked out to (Name)', row)
        print(f"checkedOutTo == {checkedOutTo}")

        if checkedOutTo:
            #Step 4a: Mark this asset as returned
            print(f"{assetId} was checked out to {checkedOutTo[0][0]} but {userName} returned it.")
            self.clearCellByName('Checked out to (Name)', row)
            return f"{assetId.split('-')[2]} returned"
        else:
            #Step 4b: Mark this asset as being used by userName
            print(f"{assetId} is checked out to {userName}")
            self.writeCellByName('Checked out to (Name)', row, userName)
            return f"{assetId.split('-')[2]} checked out to {userName}"

if __name__ == "__main__":
    ET1 = nubiInventory()
    print(f"{ET1.run('Scott', 'NUBI-ET1-TestCode0001')}")
