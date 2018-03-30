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

from confession_manager import ConfessionManager
from confession_manager_exceptions import UnavailableResourseError

# ==================================================== CONSTANTS ===================================================== #


def main():
    try:
        server = ConfessionManager()
        server.run()
    except KeyboardInterrupt:
        del server
    except UnavailableResourseError:
        # TODO: Print indicating message
        pass

if __name__ == "__main__":
    main()
