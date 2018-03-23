#! /usr/bin/python
# -*- encoding: utf-8 -*-
# ==================================================================================================================== #
# File          : google.py
# Purpose       : A client for Google sheets, providing basic spreadsheet editing capabillities
# Author        : Cory Levy
# Date          : 2017/02/25
# ==================================================================================================================== #
# ===================================================== IMPORTS ====================================================== #
# ===================================================== CLASSES ====================================================== #


class UnavailableResourseError(Exception):
    """
    Thrown when trying to acquire the Google Sheets lock
    """
    pass
