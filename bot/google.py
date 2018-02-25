# =================================================================================================================== #
# File          : google.py
# Purpose       : A client for Google sheets, providing basic spreadsheet editing capabillities
# Author        : Cory Levy
# Date          : 2017/02/25
# =================================================================================================================== #
# ===================================================== IMPORTS ====================================================== #

import httplib2

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# ==================================================== CONSTANTS ===================================================== #

CREDENTIALS_FILE_PATH = ""
CONFESSION_SHEET_ID = "1eyPP0nEnivMe9fS_y1Z8EKwY02f8rETxKK1RmaRlKYs"
CONFESSIONS_FORM_RANGE_A1_FORMAT = "Form Responses 1!B:C"

RAW_INPUT_OPTION = "RAW"
PARSE_DATA_INPUT_OPTION = "USER_ENTERED"

# ===================================================== CLASSES ====================================================== #


class Sheet(object):
    """
    """
    def __init__(self, sheet_id):
        """
        """
        # Load credentials file
        store = Storage(CREDENTIALS_FILE_PATH)
        self.credentials = store.get()
        self.id = sheet_id

        # Create the connection to Google Sheets
        self.connection = self.credentials.authorize(httplib2.Http())
        discovery_url = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
        self.service = discovery.build('sheets', 'v4', http=self.connection, discoveryServiceUrl=discovery_url)

    def get_data(self, data_range):
        """
        """
        # Get data from sheet
        result = self.service.spreadsheets().values().get(spreadsheetId=self.id, range=data_range).execute()
        return result.get("values", [])

    def add_row(self, data, data_range, input_option_raw=True):
        """
        """
        input_option = RAW_INPUT_OPTION if input_option_raw else PARSE_DATA_INPUT_OPTION

        body = {
            "values": data
        }

        self.service.spreadsheets().values().append(spreadsheetId=self.id,
                                                    range=data_range,
                                                    valueInputOption=input_option,
                                                    body=body).execute()


class ConfessionsSheet(Sheet):
    """
    """
    def get_ready_confessions(self):
        """
        """
        raw_confessions = self.get_data(CONFESSIONS_FORM_RANGE_A1_FORMAT)
        confessions = [confession for confession in raw_confessions if len(confession) > 1]
        return confessions

    def archive_confession(self, date_received, date_published, confession):
        """
        """
        row = [date_received, date_published, confession]
        self.add_row(list(row))
