#! /usr/bin/python
# -*- encoding: utf-8 -*-
# ==================================================================================================================== #
# File          : facebook_connector.py
# Purpose       : A client for Facebook pages, providing basic page operations.
# Author        : Dor Aharonson, Cory Levy
# Date          : 2017/02/26
# ==================================================================================================================== #
# ===================================================== IMPORTS ====================================================== #

import facebook

# ==================================================== CONSTANTS ===================================================== #

PAGE_ID = "332027507300337"
ACCESS_TOKEN = "EAAWXm63aQDYBAM75MY1WBvZA7M3gXDB9GwWzhAaBwtd1Qfr7LFjv4cv1z0KHpUv97upM9HEVDR3wImgmUP2FShh6VjTVJ8mDNqQV0DLoWeEmzL6RAsrQeoebulaiepWajTPW9XnV9WJh0ZCyfCxbuZCxeOh9O9ZA2UbJ2lpxB3J09EhZBaSkF"
POST_FORMAT = ""

# ===================================================== CLASSES ====================================================== #


class FacebookPage(object):
    """
    Represents a facebook page, allows posting to the page as the page.
    """
    def __init__(self, page_id, access_token):
        '''
        :param page_id: the page id as shown in the page->about
        :param access_token: the access token from Facebook Graph (explanation: http://nodotcom.org/python-facebook-tutorial.html)
        '''
        self.page = facebook.GraphAPI(access_token)

    def post(self, msg):
        '''
        Posts a message on the page's wall.
        :param msg: The message
        '''
        status = self.page.put_wall_post(msg)
        return status


class IDFConfessionsPage(FacebookPage):
    """
    """
    @property
    def _last_post_number(self):
        """
        """
        return 1

    def post(self, confession):
        """
        """
        post = POST_FORMAT
        super(IDFConfessionsPage, self).post(post) 
