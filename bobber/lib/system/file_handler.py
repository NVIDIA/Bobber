# SPDX-License-Identifier: MIT
import os
from typing import NoReturn


def create_directory(directory: str) -> NoReturn:
    """
    Create a directory if it doesn't exist.

    Parameters
    ----------
    directory : string
        A ``string`` of the full directory path to create if it doesn't exist.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def update_log(logfile: str, contents: str) -> NoReturn:
    """
    Append a log with new output from a test.

    Parameters
    ----------
    logfile : string
        A ``string`` of the logfile to write data to.
    contents : string
        A ``string`` of the contents to append the log file with.
    """
    with open(logfile, 'a') as log:
        log.write(contents)
