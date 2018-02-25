# =================================================================================================================== #
# File          : google.py
# Purpose       : A client for Google sheets, providing basic spreadsheet editing capabillities
# Author        : Cory Levy
# Date          : 2017/02/25
# =================================================================================================================== #
# ===================================================== IMPORTS ====================================================== #

import os
import httplib2

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# ==================================================== CONSTANTS ===================================================== #

CREDENTIALS_FILE_PATH = os.path.expanduser("~/client_secret.json")
CONFESSION_SHEET_ID = "1eyPP0nEnivMe9fS_y1Z8EKwY02f8rETxKK1RmaRlKYs"
READY_CONFESSIONS_A1_FORMAT = "Form Responses 1!A:C"
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
APPLICATION_NAME = 'Confession Manager'

SHEETS_API_URL = "https://sheets.googleapis.com/$discovery/rest?version=v4"
ROWS_DIMENSION = "ROWS"
ARCHIVE_RANGE = "Archive!A:C"

RAW_INPUT_OPTION = "RAW"
PARSE_DATA_INPUT_OPTION = "USER_ENTERED"

DATE_PUBLISHED_DICT_KEY = "Date Published"
CONFESSION_DICT_KEY = "Confession"

# ===================================================== CLASSES ====================================================== #


class Sheet(object):
    """
    Represent a sheet, provides basic read/write operations.
    """
    def __init__(self, sheet_id):
        """
        @param sheet_id: The id of the sheet, found in the google sheet web view.
        @type sheet_id: str
        """
        # Load credentials file
        self.credentials = self._get_credentials()
        self.id = sheet_id

        # Create the connection to Google Sheets
        self.connection = self.credentials.authorize(httplib2.Http())
        discovery_url = (SHEETS_API_URL)
        self.service = discovery.build('sheets', 'v4', http=self.connection, discoveryServiceUrl=discovery_url)

    def _get_credentials(self):
        """
        Gets valid user credentials from storage. If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.
        @return: The obtained credentials.
        @rtype
        """
        # Make sure the credentials directory exists
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, "google_sheets.json")

        # Try loading credentials from file
        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            # Perform authentication
            flow = client.flow_from_clientsecrets(CREDENTIALS_FILE_PATH, SCOPES)
            flow.user_agent = APPLICATION_NAME
            credentials = tools.run_flow(flow, store)

        return credentials

    def get_data(self, data_range):
        """
        Get data from the sheet.
        @param data_range: The cells of the spreadsheet to retrieve. Specified in A1 format.
        @type data_range: str
        @return: The retrieved data
        @rtype: list
        """
        # Get data from sheet
        result = self.service.spreadsheets().values().get(spreadsheetId=self.id, range=data_range).execute()
        return result.get("values", [])

    def add_row(self, data, data_range, raw_input_option=True):
        """
        """
        input_option = RAW_INPUT_OPTION if raw_input_option else PARSE_DATA_INPUT_OPTION

        # Construct the request parameters
        body = {
            "values": data
        }

        self.service.spreadsheets().values().append(spreadsheetId=self.id,
                                                    range=data_range,
                                                    valueInputOption=input_option,
                                                    body=body).execute()

    def delete_row(self, row_number):
        """
        """
        body = {
            "deleteDimension": {
                "range": {
                    "sheetId": self.id,
                    "dimension": ROWS_DIMENSION,
                    "startIndex": row_number - 1,
                    "endIndex": row_number - 1
                }
            }
        }
        raise NotImplementedError


class ConfessionsSheet(Sheet):
    """
    A sheet object tailored specifically for the confession spreadsheet.
    """
    def get_ready_confessions(self):
        """
        Return the confessions marked for publishing
        """
        raw_confessions = self.get_data(READY_CONFESSIONS_A1_FORMAT)

        # Check if the confession is marked for publishing
        confessions = [confession for confession in raw_confessions if len(confession) > 1]
        
        processed_confessions = []
        for confession in confessions:
            data = {}
            data[DATE_PUBLISHED_DICT_KEY] = confession[0]
            data[CONFESSION_DICT_KEY] = confession[1]
            
            processed_confessions.append(data)

        return processed_confessions

    def add_to_archive(self, date_received, date_published, confession):
        """
        """
        row = [date_received, date_published, confession]
        self.add_row(list(row), ARCHIVE_RANGE)
