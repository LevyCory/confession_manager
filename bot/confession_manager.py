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
import Queue

import google_connector
import facebook_connector

# ==================================================== CONSTANTS ===================================================== #

CONFESSION_MANAGER_DIRECTORY = os.path.expanduser("~/.confessions")
PUBLISH_LIST_FILE_NAME = "confessions.json"
FILE_NOT_FOUND_ERRNO = 2

# ===================================================== CLASSES ====================================================== #


class SerializableQueue(Queue.Queue):
    """
    A queue that can be easily written and read from the disk
    """
    def __init__(self, backup_file):
        """
        @param backup_file: A file to backup the queue to.
        @type backup_file: str
        """
        super(SerializableQueue, self).__init__()
        self.backup_file = backup_file

        # Try restoring previous data if backup exists
        try:
            with open(self.backup_file, "r") as queue_file:
                self.queue = pickle.load(queue_file)

        except IOError as error:
            if error.errno == FILE_NOT_FOUND_ERRNO:
                # Create the backup file
                try:
                    open(self.backup_file, "w").close()
                except IOError:
                    pass

    @property
    def size(self):
        """
        @return: Number of elements in the queue.
        @rtype: int
        """
        return len(self.queue)

    def backup(self):
        """
        Back up the queue to the disk.
        """
        if self.size > 0:
            with open(self.backup_file, "w") as queue_file:
                pickle.dump(queue_file, self.queue)

    def restore(self):
        """
        Restore queue from backup
        """
        try:
            with open(self.backup_file, "r") as queue_file:
                self.queue = pickle.load(queue_file)
        except OSError:
            pass


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

        self.queue = SerializableQueue(self.backup_file)

    def _process_spreadsheet(self):
        """
        Process the spread sheet:
        Move posted marked with 'x' to the graveyard.
        Move posted marked with 'a' to the archive.
        Publish posts marked with 'v'.
        """
        confessions = self.get_ready_confessions(google_connector.GRAVEYARD_MODE)
        self._add_confessions_to_table(confessions, google_connector.GRAVEYARD_RANGE)

        confessions = self.get_ready_confessions(google_connector.ARCHIVE_MODE)
        self._add_confessions_to_table(confessions, google_connector.ARCHIVE_MODE)

        return self.get_ready_confessions(google_connector.PUBLISH_MODE)

    def _publish_queue(self):
        """
        Publish the queue to IDF Confessions
        """
        while not self.queue.empty():
            self.page.post(self.queue.get())
            time.sleep(8)

    def run(self):
        """
        Run the server
        """
        try:
            while True:
                try:
                    # Get confessions to post.
                    ready_confessions = self._process_spreadsheet()
                    self.queue.deque.extend(ready_confessions)

                    # Publish confessions
                    self._publish_queue()

                    # Archive confessions
                    self.confessions.archive_confessions(ready_confessions)

                except KeyboardInterrupt:
                    raise

                except Exception:
                    # TODO: Use logging
                    print "Critical error occoured."
                    # Give the server some time to think
                    time.sleep(60)

        except KeyboardInterrupt:
            self.queue.backup()


if __name__ == "__main__":
    server = ConfessionManager()
    server.run()
