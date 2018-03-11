#! /usr/bin/python
# -*- encoding: utf-8 -*-
# ==================================================================================================================== #
# File          : confession_manager.py
# Purpose       : Runs the whole operation
# Author        : Cory Levy
# Date          : 2017/02/25
# ==================================================================================================================== #
# ===================================================== IMPORTS ====================================================== #

import os
import time
import pickle

import google_connector
from google_connector import ARCHIVE_RANGE, GRAVEYARD_RANGE
import facebook_connector

# ==================================================== CONSTANTS ===================================================== #

CONFESSION_MANAGER_DIRECTORY = os.path.expanduser("~/.confessions")
PUBLISH_LIST_FILE_NAME = "confessions.pickle"
FILE_NOT_FOUND_ERRNO = 2

# ===================================================== CLASSES ====================================================== #


class ConfessionManager(object):
    """
    Takes confessions from Google Sheets and posts them to Facebook
    """
    def __init__(self):
        self.confessions = google_connector.ConfessionsSheet()
        self.page = facebook_connector.IDFConfessionsPage()
        self.backup_file = os.path.join(CONFESSION_MANAGER_DIRECTORY, PUBLISH_LIST_FILE_NAME)

        try:
            os.makedirs(CONFESSION_MANAGER_DIRECTORY)
        except OSError:
            pass

        try:
            with open(self.backup_file, "r") as backup_file:
                self.queue = pickle.load(backup_file)
        except (IOError, EOFError):
            self.queue = []

    def _process_spreadsheet(self):
        """
        Process the spread sheet:
        Move posted marked with 'x' to the graveyard.
        Move posted marked with 'a' to the archive.
        Publish posts marked with 'v'.
        """
        confessions = self.confessions.get_confessions(google_connector.GRAVEYARD_MODE)
        self.confessions.move_confessions(confessions, GRAVEYARD_RANGE)
        time.sleep(2)

        confessions = self.confessions.get_confessions(google_connector.ARCHIVE_MODE)
        self.confessions.move_confessions(confessions, ARCHIVE_RANGE)
        time.sleep(2)

        return self.confessions.get_confessions(google_connector.PUBLISH_MODE)

    def _publish_queue(self):
        """
        Publish the queue to IDF Confessions
        """
        for confession in self.queue:
            self.page.post(confession)
            time.sleep(8)

    def run(self):
        """
        Run the server
        """
        print "Confession Manager is now Running."
        try:
            while True:
                # Get confessions to post.
                if len(self.queue) == 0:
                    self.queue = self._process_spreadsheet()

                # Publish confessions
                self._publish_queue()

                # Archive confessions
                self.confessions.move_confessions(self.queue, ARCHIVE_RANGE)
                self.queue = []

                time.sleep(10)

        except KeyboardInterrupt:
            try:
                if len(self.queue) != 0:
                    with open(self.backup_file, "w") as backup_file:
                        pickle.dump(self.queue, backup_file)
                else:
                    os.remove(self.backup_file)

            except (IOError, OSError):
                pass


if __name__ == "__main__":
    while True:
        try:
            server = ConfessionManager()
            server.run()
        except Exception as e:
            print e
        time.sleep(60)
