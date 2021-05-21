# SPDX-License-Identifier: MIT
import re
from collections import defaultdict
from typing import Tuple


class bcolors:
    """
    A helper class to annotate text with colors.
    """
    PASS = '\033[92m'  # nosec
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'


def num_systems(log: str) -> int:
    """
    Returns an ``integer`` of the number of systems that were tested during a
    particular run.

    Parameters
    ----------
    log : str
        A ``string`` of the filename for a single log.

    Returns
    -------
    int
        Returns an ``int`` of the number of systems that were tested for the
        given logfile. Defaults to None if not found.
    """
    try:
        systems = re.findall(r'systems_\d+_', log)
        systems = re.findall(r'\d+', systems[0])
        return int(systems[0])
    except ValueError:
        return None


def _bobber_version(log: str) -> str:
    """
    Returns a ``string`` representation of the Bobber version tested, such as
    '6.3.0'.

    Parameters
    ----------
    log : str
        A ``string`` of the filename for a single log.

    Returns
    -------
    str
        Returns a ``string`` of the Bobber version tested, such as '6.3.0'.

    Raises
    ------
    ValueError
        Raises a ``ValueError`` if the version cannot be parsed from the log
        file.
    """
    version = re.findall(r'version_\d+_\d+_\d+', log)
    if len(version) != 1:
        raise ValueError(f'Could not parse Bobber version from {log} file!')
    version = version[0].replace('version_', '')
    return version.replace('_', '.')


def check_bobber_version(logs: list, override: bool) -> str:
    """
    Ensure the Bobber version matches in all logs being parsed.

    As a safeguard to mixing results from different Bobber versions, the
    version needs to be checked for all logs to ensure they are equal. By
    comparing each new log version with the previous version captured, if all
    are equal in the list of logs, then it is guaranteed that the logs are all
    the same.

    Parameters
    ----------
    logs : list
        A ``list`` of strings of all of the log filenames in the directory that
        was passed.
    override : bool
        A ``boolean`` which evaluates to ``True`` when the version-checking
        should be skipped.

    Returns
    -------
    str
        Returns a ``string`` of the Bobber version being tested.

    Raises
    ------
    ValueError
        Raises a ``ValueError`` when any log versions don't match.
    """
    last_version = None

    for log in logs:
        version = _bobber_version(log)
        if override:
            return version
        if last_version and version != last_version:
            raise ValueError('Error: Only logs using the same Bobber version '
                             'are allowed in the results directory.')
        last_version = version
    return version


def _convert_to_bytes(value: str) -> float:
    """
    Convert a number to bytes.

    Convert a passed number to bytes by parsing the number from the passed
    string and multiplying by the appropriate multiplier to convert from a
    larger unit to bytes.

    Parameters
    ----------
    value : str
        A ``string`` of the value to convert to bytes.

    Returns
    -------
    float
        Returns a ``float`` of the final value in bytes.
    """
    number = float(re.sub('[a-zA-Z]*', '', value))
    if 'gib' in value.lower():
        return number * 1024 * 1024 * 1024
    elif 'g' in value.lower():
        return number * 1e9
    elif 'mib' in value.lower():
        return number * 1024 * 1024
    elif 'm' in value.lower():
        return number * 1e6
    elif 'kib' in value.lower():
        return number * 1024
    elif 'k' in value.lower():
        return number * 1e3


def _fio_command_parse(command: str) -> dict:
    """
    Parse the command parameters for fio.

    Pull all of the flags and parameters used during a fio run and save them as
    a dictionary to make it easier to reference what was used during a test.

    Parameters
    ----------
    command : str
        A ``string`` of the command used during the fio run.

    Returns
    -------
    dict
        Returns a ``dictionary`` of the parameters used during the fio run.
    """
    parameter_dict = {}

    for parameter in command.split():
        # Skip the following parameters as they don't provide meaningful data.
        if parameter == '/usr/bin/fio':
            continue
        key, value = parameter.split('=')
        key = key.replace('--', '')
        if key in ['blocksize', 'size']:
            value = _convert_to_bytes(value)
        else:
            # Attempt to convert to a int for numerical values. If it fails,
            # keep as a string as that's likely intended type.
            try:
                value = int(value)
            except ValueError:
                value = str(value)
        parameter_dict[key] = value
    return parameter_dict


def _compare_dicts(old_results: dict, new_results: dict) -> bool:
    """
    Compare testing dictionaries for equality.

    Compare the dictionaries for equality while ignoring the 'directory' and
    'command' keys since these will always differ amongst tests. If all other
    parameters are equal, it is assumed the tests used the same parameters.

    Parameters
    ----------
    old_results : dict
        A ``dictionary`` of the test parameters used during the
        previously-parsed test log.
    new_results : dict
        A ``dictionary`` of the test parameters used during the test log
        currently being parsed.

    Returns
    -------
    bool
        Returns a ``boolean`` which evaluates to `True` when all of the
        parameters are equal between the two dictionaries and `False` if at
        least on parameter is different.
    """
    ignore_keys = ['directory', 'command']

    old = dict((k, v) for k, v in old_results.items() if k not in ignore_keys)
    new = dict((k, v) for k, v in new_results.items() if k not in ignore_keys)
    return old == new


def fio_command_details(log_contents: str, old_reads: dict,
                        old_writes: dict) -> Tuple[dict, dict]:
    """
    Parse the command parameters and compare with the previous log.

    Pull the fio parameters used for both the read and write commands during
    the tests and compare them with the previous log file that was parsed to
    ensure all tests being parsed are using the same parameters.

    Parameters
    ----------
    log_contents : str
        A ``string`` of all the output inside a log file.
    old_reads : dict
        A ``dictionary`` of the previous read test parameters that were parsed.
    old_writes : dict
        A ``dictionary`` of the previous write test parameters that were
        parsed.

    Returns
    -------
    tuple
        Returns a ``tuple`` of (``dict``, ``dict``) where each dictionary are
        the parsed read and write parameters, respectively, from the tests.

    Raises
    ------
    ValueError
        Raises a ``ValueError`` if the fio command type is unexpected or the
        parameters differ between two or more tests.
    """
    commands = re.findall(r'/usr/bin/fio --rw.*', log_contents)
    if len(commands) < 2:
        raise ValueError(f'FIO command not found in {log} file!')

    for command in commands:
        if '--rw=read' in command:
            read_params = _fio_command_parse(command)
            read_params['command'] = command
        elif '--rw=write' in command:
            write_params = _fio_command_parse(command)
            write_params['command'] = command
        elif '--rw=randread' in command:
            read_params = _fio_command_parse(command)
            read_params['command'] = command
        elif '--rw=randwrite' in command:
            write_params = _fio_command_parse(command)
            write_params['command'] = command
        else:
            raise ValueError('Unexpected FIO test type. Expected '
                             'read, write, randread, or randwrite.')
    if old_reads and old_writes:
        if not _compare_dicts(old_reads, read_params) or \
           not _compare_dicts(old_writes, write_params):
            raise ValueError('Parameters differ between tests. Ensure only '
                             'tests with the same parameters are used.')
    return read_params, write_params


def divide_logs_by_systems(log_files: list, log_to_match: str) -> dict:
    """
    Extract logs on a per-system basis.

    Given a list of all logs in a directory and a string to match for the log
    files, extract all of the requested logs and group them together on a
    per-system basis. For example, matching 'stg_iops' will pull all of the
    IOPS test logs and combine all of the one-node IOPS logs in a list, then
    all of the two-node IOPS logs in another list, and so on.

    Parameters
    ----------
    log_files : list
        A ``list`` of log filenames from the passed directory to parse.
    log_to_match : str
        A ``string`` of the logs to match in the directory. 'stg_iops' will
        match all logs that begin with 'stg_iops'.

    Returns
    -------
    dict
        Returns a ``dictionary`` of all results where the key is the number of
        nodes being tested and the value is a list of all of the logs that
        match the filter for that system count.
    """
    # Divide the results based on the number of systems tested.
    num_systems_dict = defaultdict(list)

    for log in log_files:
        if log_to_match not in log:
            continue
        systems = num_systems(log)
        num_systems_dict[systems].append(log)
    return num_systems_dict
