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
import random
import datetime

import google_connector
import facebook_connector
from google_connector import ARCHIVE_RANGE, GRAVEYARD_RANGE
from confession_manager_exceptions import UnavailableResourseError

# ==================================================== CONSTANTS ===================================================== #

HOME_DIRECTORY = os.path.expanduser("~")
CONFESSION_MANAGER_DIRECTORY = os.path.join(HOME_DIRECTORY, ".confessions")
PUBLISH_LIST_FILE_NAME = "confessions.pickle"

FILE_NOT_FOUND_ERRNO = 2
MIN_CONFESSION_COUNT = 5
MAX_CONFESSION_COUNT = 8
MIN_TIMEOUT_MINUTES = 30
MAX_TIMEOUT_MINUTES = 50
TWELVE_AM = 24
SEVEN_AM = 7

# ===================================================== CLASSES ====================================================== #


class ConfessionManager(object):
    """
    Takes confessions from Google Sheets and posts them to Facebook
    """
    def __init__(self):
        self.confessions = google_connector.ConfessionsSheet()
        try:
            pass
            # self.confessions.lock()
        except UnavailableResourseError:
            raise UnavailableResourseError("Another instance of Confession Manager is running. It must be shut down "
                    "before running another one")

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

    def __del__(self):
        try:
            del self.confessions
        except Exception:
            pass

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
        last_publish_time = datetime.datetime.now()
        offline_queue_timeout_minutes = random.randint(MIN_TIMEOUT_MINUTES, MAX_TIMEOUT_MINUTES)

        print "Confession Manager is now Running."

        try:
            while True:
                current_time = datetime.datetime.now()

                # Get confessions to post.
                if len(self.queue) == 0:
                    self.queue = self._process_spreadsheet()

                # Check how much time has passed since the last posting session
                elapsed_time_minutes = (current_time - last_publish_time).seconds / 60

                if TWELVE_AM >= current_time.hour >= SEVEN_AM and elapsed_time_minutes > offline_queue_timeout_minutes:
                    # Get confessions from the offline queue
                    queued_confessions = self.confessions.get_confessions(google_connector.QUEUE_MODE)

                    # Perform the next steps only if there were queued confessions to prevent waiting too much
                    if len(queued_confessions) != 0:
                        try:
                            # Post a random number of confessions from the queue
                            queued_confessions = queued_confessions[:random.randint(MIN_CONFESSION_COUNT, MAX_CONFESSION_COUNT)]
                        except IndexError:
                            pass

                        self.queue.extend(queued_confessions)
                        last_publish_time = current_time

                        offline_queue_timeout_minutes = random.randint(MIN_TIMEOUT_MINUTES, MAX_TIMEOUT_MINUTES)

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

        except KeyboardInterrupt:
            break

        except UnavailableResourseError as e:
            print e
            break

        except Exception as e:
            print e
        time.sleep(60)
