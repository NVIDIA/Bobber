# SPDX-License-Identifier: MIT
import os
import yaml
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


def write_file(filename: str, contents: str) -> NoReturn:
    """
    Write data to a file.

    Parameters
    ----------
    filename : string
        A ``string`` of the file to write data to.
    contents : string
        A ``string`` of the contents to write to the file.
    """
    with open(filename, 'w') as fp:
        fp.write(contents)


def read_yaml(filename: str) -> dict:
    """
    Read a YAML file and return the contents.

    Parameters
    ----------
    filename : string
        A ``string`` of the full file path to read.

    Returns
    -------
    dict
        Returns a ``dict`` representing the entire contents of the file.
    """
    with open(filename, 'r') as handler:
        return yaml.safe_load(handler)
