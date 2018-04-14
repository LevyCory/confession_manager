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

# ==================================================== CONSTANTS ===================================================== #

LOG_ROTATION_INTERVAL = "midnight"
CONSOLE_LOGGING_FORMAT = "%(asctime)s - %(levelbame)s - $(message)s"
FILE_LOGGING_FORMAT = "%(asctime)s - %(levelbame)s: [$(pathname)s] - $(message)s"

# ===================================================== CLASSES ====================================================== #

def setup_logger(folder, filename, verbose=False):
    """
    """
    logger = logging.getLogger()

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

    logger.setLevel(logging.debug)
