#! /usr/bin/python
# -*- encoding: utf-8 -*-
# ==================================================================================================================== #
# File          : confession_manager.py
# Purpose       : Runs the whole operation
# Author        : Cory Levy
# Date          : 2017/02/25
# ==================================================================================================================== #
# ===================================================== IMPORTS ====================================================== #

import time
import random
import socket
import logging
import datetime

import google_connector
import facebook_connector
from google_connector import ARCHIVE_RANGE, GRAVEYARD_RANGE
from confession_manager_exceptions import UnavailableResourseError

# ==================================================== CONSTANTS ===================================================== #

SECONDS_IN_MINUTE = 60
DUPLICATE_DELETION_TIMEOUT_MINUTES = 30
FILE_NOT_FOUND_ERRNO = 2
MIN_CONFESSION_COUNT = 2
MAX_CONFESSION_COUNT = 4
MIN_TIMEOUT_MINUTES = 60
MAX_TIMEOUT_MINUTES = 70
TWELVE_AM = 23
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
            # TODO: Fix
            # self.confessions.lock()
        except UnavailableResourseError:
            raise UnavailableResourseError("Another instance of Confession Manager is running. It must be shut down "
                    "before running another one")

        self.page = facebook_connector.IDFConfessionsPage()
        self.queue = []

    def __del__(self):
        try:
            self.confessions.release()
            del self.confessions
        except Exception:
            pass

    def _delete_confessions(self):
        """
        """
        logging.debug("Deleting confessions mark with 'X'")
        confessions = self.confessions.get_confessions(google_connector.GRAVEYARD_MODE)
        time.sleep(1)
        self.confessions.move_confessions(confessions, GRAVEYARD_RANGE)

    def _archive_confessions(self):
        """
        """
        logging.debug("Archiving confessions")
        confessions = self.confessions.get_confessions(google_connector.ARCHIVE_MODE)
        time.sleep(1)
        self.confessions.move_confessions(confessions, ARCHIVE_RANGE)

    def _publish_queue(self):
        """
        Publish the queue to IDF Confessions
        """
        logging.debug("Publishing confessions from queue")
        for confession in self.queue:
            self.page.post(confession)
            time.sleep(8)

    def run(self):
        """
        Run the server
        """
        last_publish_time = datetime.datetime.now()
        last_duplicate_deletion_time = datetime.datetime.now()
        offline_queue_timeout_minutes = random.randint(MIN_TIMEOUT_MINUTES, MAX_TIMEOUT_MINUTES)

        print "Confession Manager is now Running."

        while True:
            try:
                current_time = datetime.datetime.now()

                # Delete duplicate posts every 30 minutes
                time_since_duplicate_deletion = (current_time - last_duplicate_deletion_time).seconds / SECONDS_IN_MINUTE
                if time_since_duplicate_deletion > DUPLICATE_DELETION_TIMEOUT_MINUTES:
                    self.confessions.delete_duplicates()

                # Re arrange the confession sheet
                self._delete_confessions()
                self._archive_confessions()

                # Get confessions to post.
                if len(self.queue) == 0:
                    self.queue = self.confessions.get_confessions(google_connector.PUBLISH_MODE)

                # Check how much time has passed since the last posting session
                elapsed_time_minutes = (current_time - last_publish_time).seconds / 60

                if TWELVE_AM >= current_time.hour >= SEVEN_AM and elapsed_time_minutes > offline_queue_timeout_minutes:
                    # Get confessions from the offline queue
                    queued_confessions = self.confessions.get_confessions(google_connector.QUEUE_MODE)

                    # Perform the next steps only if there were queued confessions to prevent waiting too much
                    if len(queued_confessions) != 0:
                        try:
                            # Post a random number of confessions from the queue
                            queued_confessions = queued_confessions[:random.randint(MIN_CONFESSION_COUNT,
                                MAX_CONFESSION_COUNT)]
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

            except socket.timeout:
                self.confessions.reconnect()

            except KeyboardInterrupt:
                print "Finishing session..."
                raise

            except Exception as exception:
                print exception
                time.sleep(30)

