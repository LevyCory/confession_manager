#! /usr/bin/python
# -*- encoding: utf-8 -*-
# ==================================================================================================================== #
# File          : google.py
# Purpose       : A client for Google sheets, providing basic spreadsheet editing capabillities
# Author        : Cory Levy
# Date          : 2017/02/25
# ==================================================================================================================== #
# ===================================================== IMPORTS ====================================================== #

import os
import httplib2
import datetime

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from confession_manager_exceptions import UnavailableResourseError

# ==================================================== CONSTANTS ===================================================== #

HOME_DIRECTORY = os.path.expanduser("~")
CREDENTIALS_FILE_PATH = os.path.join(HOME_DIRECTORY, "client_secret.json")
CONFESSIONS_SPREADSHEET_ID = "1eyPP0nEnivMe9fS_y1Z8EKwY02f8rETxKK1RmaRlKYs"
CONFESSION_SHEET_ID = "444158458"
LOCK_SHEET_ID = "742924914"
ARCHIVE_SHEET_ID = "1557599273"
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
SHEETS_API_URL = "https://sheets.googleapis.com/$discovery/rest?version=v4"
APPLICATION_NAME = 'Confession Manager'

CONFESSION_READY_LENGTH = 3
ROWS_DIMENSION = "ROWS"
READY_CONFESSIONS_A1_FORMAT = "Form Responses 1!A:C"
ARCHIVE_RANGE = "Archive!A:C"
GRAVEYARD_RANGE = "Graveyard!A:C"
LOCK_FORMAT = "Lock!A1"
LOCK_DATA = "Confession Manager Lock"
PUBLISHED_TIME_FORMAT = "%m/%m/%Y %H:%M:%S"

RAW_INPUT_OPTION = "RAW"
PARSE_DATA_INPUT_OPTION = "USER_ENTERED"

DATE_PUBLISHED_DICT_KEY = "Date Published"
CONFESSION_DICT_KEY = "Confession"
LINE_NUMBER_DICT_KEY = "Line Number"

DATE_RECEIVED_INDEX = 0
CONFESSION_INDEX = 1

GRAVEYARD_MODE = "x"
ARCHIVE_MODE = "a"
PUBLISH_MODE = "v"
QUEUE_MODE = "q"

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
        self.id = sheet_id

        # Load credentials file
        self.credentials = self._get_credentials()

        # Create the connection to Google Sheets
        self.connection = self.credentials.authorize(httplib2.Http())
        discovery_url = (SHEETS_API_URL)
        self.service = discovery.build('sheets', 'v4', http=self.connection, discoveryServiceUrl=discovery_url)

    def __del__(self):
        """
        """
        if self.has_lock:
            self.release()

    def _get_credentials(self):
        """
        Gets valid user credentials from storage. If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.
        @return: The obtained credentials.
        """
        # Make sure the credentials directory exists. If not, create it and store the credentials in there.
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
        Add a row to a specified sheet.
        @param data: The data to add to the sheet.
        @type data: list
        @param data_range: The cell range to insert the data into. Must be in A1 format.
        @type data_range: str
        @param raw_input_option: Whether to parse the data or not. If set to true, the string "2 * 4" will
                                 be inserted as 8, otherwise as "2 * 4".
        @type raw_input_option: bool
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

    def delete_rows(self, sheet_id, rows):
        """
        Delete rows by line numbers.
        @param sheet_id: The worksheet inside the spreadsheet to delete the rows from.
        @type sheet_id: str
        @param rows: The row numbers to delete.
        @type rows: list
        """
        if len(rows) == 0:
            return None

        # Sort in decending order and remove duplicates
        rows = sorted(list(set(rows)), reverse=True)

        body = {
            "requests": []
        }

        # Construct the requests for each row
        for row in rows:
            delete_row_request = {
                "deleteDimension": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": ROWS_DIMENSION,
                        "startIndex": row - 1,
                        "endIndex": row
                    }
                }
            }

            body["requests"].append(delete_row_request)

        # Send requests
        self.service.spreadsheets().batchUpdate(spreadsheetId=self.id, body=body).execute()


class ConfessionsSheet(Sheet):
    """
    A sheet object tailored specifically for the confession spreadsheet.
    """
    def __init__(self):
        super(ConfessionsSheet, self).__init__(CONFESSIONS_SPREADSHEET_ID)
        self.has_lock = False

    def get_confessions(self, mode):
        """
        Return the confessions marked for publishing
        """
        raw_confessions = self.get_data(READY_CONFESSIONS_A1_FORMAT)

        processed_confessions = []
        for number, confession in enumerate(raw_confessions):
            # Confessions marked for publishing have a cell extra in their representing list
            try:
                if confession[2].lower() == mode:
                    data = {
                        DATE_PUBLISHED_DICT_KEY: confession[DATE_RECEIVED_INDEX].encode("utf-8"),
                        CONFESSION_DICT_KEY: confession[CONFESSION_INDEX].encode("utf-8"),
                        LINE_NUMBER_DICT_KEY: number + 1
                    }
                    processed_confessions.append(data)

            except IndexError:
                continue

        return processed_confessions

    def move_confessions(self, confessions, destinstaion):
        """
        Add confessions to the archive and delete them from the confession pool.
        @param confessions: A list of confessions.
        @type confessions: list
        """
        self._add_confessions_to_table(confessions, destinstaion)
        self._delete_confessions_from_pool(confessions)

    def delete_duplicates(self):
        """
        Delete confessions that appear in more than one line
        """
        duplicates = self._get_duplicate_confessions()

        # Make sure there is one confession left of each duplicate
        for confession in duplicates:
            duplicates[confession].pop()

        blacklist = []
        for lines in duplicates.values():
            blacklist.extend(lines)

        self.delete_rows(CONFESSION_SHEET_ID, blacklist)

    def _get_duplicate_confessions(self):
        """
        Get the confession that were sent more than one time.
        @return: A dict mapping a confession to the lines it appears at.
        @rtype: dict
        """
        confessions_lines = {}
        duplicate_confessions = {}

        raw_confessions = self.get_data(READY_CONFESSIONS_A1_FORMAT)

        # Map confessions to lines
        for index, confession in enumerate(raw_confessions):
            try:
                try:
                    confessions_lines[confession[1]].append(index + 1)
                except IndexError:
                    pass
            except KeyError:
                try:
                    confessions_lines[confession[1]] = [index + 1]
                except IndexError:
                    pass

        # Leave only the confessions with more than one line
        for confession, lines in confessions_lines.iteritems():
            if len(lines) > 1:
                duplicate_confessions[confession] = lines

        return duplicate_confessions

    def _add_confessions_to_table(self, confessions, data_range):
        """
        Add a confession row to the archive.
        @param confession: The confession to archive.
        @type confession: dict
        @param data_range: The cell range to insert the data into. Must be in A1 format.
        @type data_range: str
        """
        current_time = datetime.datetime.now()
        data = [[conf[DATE_PUBLISHED_DICT_KEY], current_time.strftime(PUBLISHED_TIME_FORMAT), conf[CONFESSION_DICT_KEY]] for conf in confessions]
        self.add_row(data, data_range)

    def _delete_confessions_from_pool(self, confessions):
        """
        Delete a list of confessions from the confession pool.
        @param confessions: The confessions to delete.
        @type confessions: dict
        """
        line_numbers = [confession[LINE_NUMBER_DICT_KEY] for confession in confessions]
        self.delete_rows(CONFESSION_SHEET_ID, line_numbers)

    def lock(self):
        """
        """
        data = self.get_data(LOCK_FORMAT)
        if not data:
            self.add_row([[LOCK_DATA]], LOCK_FORMAT)
            self.has_lock = True
        else:
            raise UnavailableResourseError("The lock could not be acquired")

    def release(self):
        """
        """
        self.delete_rows(LOCK_SHEET_ID, [1])
        self.has_lock = False
