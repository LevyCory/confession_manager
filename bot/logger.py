#! /usr/bin/python
# -*- encoding: utf-8 -*-
# ==================================================================================================================== #
# File          : logger.py
# Purpose       : Configures the logging for the Confession Manager.
# Author        : Cory Levy
# Date          : 2017/04/14
# ==================================================================================================================== #
# ===================================================== IMPORTS ====================================================== #

import os
import logging
from logging.handlers import TimedRotatingFileHandler

# ==================================================== CONSTANTS ===================================================== #

LOG_ROTATION_INTERVAL = "midnight"
CONSOLE_LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
FILE_LOGGING_FORMAT = "%(asctime)s - %(levelname)s: [%(pathname)s] - %(message)s"

# ===================================================== CLASSES ====================================================== #

def setup_logger(folder, filename, verbose=False):
    """
    """
    
    logger = logging.getLogger()

    logging.getLogger("requests").setLevel(logging.CRITICAL)
    logging.getLogger("apiclient").setLevel(logging.CRITICAL)
    logging.getLogger("oauth2client").setLevel(logging.CRITICAL)
    logging.getLogger("httplib2").setLevel(logging.CRITICAL)

    try:
        os.makedirs(folder)
    except OSError:
        # Folder exists
        pass
    
    log_file = os.path.join(folder, filename)

    file_handler = TimedRotatingFileHandler(log_file, when=LOG_ROTATION_INTERVAL)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(FILE_LOGGING_FORMAT)
    file_handler.setFormatter(file_format)
    
    console_handler = logging.StreamHandler()
    console_format = logging.Formatter(CONSOLE_LOGGING_FORMAT)

    if verbose:
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.INFO)

    console_handler.setFormatter(console_format)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.setLevel(logging.DEBUG)
