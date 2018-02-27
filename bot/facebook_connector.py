#! /usr/bin/python
# -*- encoding: utf-8 -*-
# ==================================================================================================================== #
# File          : facebook_connector.py
# Purpose       : A client for Facebook pages, providing basic page operations.
# Author        : Dor Aharonson, Cory Levy
# Date          : 2017/02/26
# ==================================================================================================================== #
# ===================================================== IMPORTS ====================================================== #

import re
import os
import json

import facebook

# ==================================================== CONSTANTS ===================================================== #

CREDENTIALS_FILE = os.path.expanduser("~/.credentials/facebook/credentials.json")
CREDENTIALS_PAGE_ACCESS_TOKEN_KEY = "idf_confessions_access_token"
CREDENTIALS_PAGE_ID_KEY = "page_id"

POST_FORMAT = "#{post_number} {text}"
POST_NUMBER_REGEX = "^#(\d+) "

POST_DATA_POSTS_KEY = "data"
POST_DATA_MESSAGE_KEY = "message"
PAGE_DATA_ID_KEY = "id"

POSTS_REQUEST_KEYWORD = "posts"

# ===================================================== CLASSES ====================================================== #


class FacebookPage(object):
    """
    Represents a facebook page, allows posting to the page as the page.
    """
    def __init__(self, page_id, access_token):
        """
        @param page_id: the page id as shown in the page->about
        @param access_token: the access token from Facebook Graph
        (explanation: http://nodotcom.org/python-facebook-tutorial.html)
        """
        self.page = facebook.GraphAPI(access_token)
        self.page_data = self.page.get_object(page_id)

    def post(self, message):
        """
        Posts a message on the page"s wall.
        @param message: The message
        """
        status = self.page.put_wall_post(message)
        return status

    def get_posts(self):
        """
        Get the last 25 posts of the page.
        @return: Last 25 posts of the page.
        @rtype: list
        """
        raw_data = self.page.get_connections(self.page_data[PAGE_DATA_ID_KEY], POSTS_REQUEST_KEYWORD)
        return raw_data[POST_DATA_POSTS_KEY]


class IDFConfessionsPage(FacebookPage):
    """
    Represent the idf confessions page
    """
    def __init__(self):
        """
        Connect and authenticate with the page.
        """
        # Load credentials from file
        try:
            with open(CREDENTIALS_FILE, "r") as creds_file:
                self.credentials = json.load(creds_file)
        except OSError:
            raise OSError("Credentials file not found in {path}".format(path=CREDENTIALS_FILE))

        super(IDFConfessionsPage, self).__init__(self.credentials[CREDENTIALS_PAGE_ID_KEY],
                                                 self.credentials[CREDENTIALS_PAGE_ACCESS_TOKEN_KEY])

    @property
    def _last_post_number(self):
        """
        @return: The last confession number.
        @rtype: int
        """
        # Parse the post number from the last post
        last_post = self.get_posts()[0][POST_DATA_MESSAGE_KEY]
        return int(re.search(POST_NUMBER_REGEX, last_post).group(1))

    def post(self, confession):
        """
        Post a confession to the page.
        @param confession: The confession to post
        @type confession: dict
        """
        post = POST_FORMAT.format(post_number=self._last_post_number + 1, text=confession["Confession"])
        super(IDFConfessionsPage, self).post(post)
