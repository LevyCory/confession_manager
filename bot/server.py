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
<<<<<<< HEAD
=======
import time
>>>>>>> ce668854c1396aa529229fa4e49260ae96e66ebb
import logging

from logger import setup_logger
from confession_manager import ConfessionManager
from confession_manager_exceptions import UnavailableResourseError

# ==================================================== CONSTANTS ===================================================== #

LOGS_DIRECTORY = os.path.join(os.curdir, "logs")
LOG_FILE_PREFIX = "confession_manager"


def main():
    setup_logger(LOGS_DIRECTORY, LOG_FILE_PREFIX)

    server = None
    try:
        server = ConfessionManager()
        server.run()
    except KeyboardInterrupt:
        del server
    except UnavailableResourseError:
        logging.error("")


if __name__ == "__main__":
    main()
