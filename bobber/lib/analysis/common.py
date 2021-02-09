# SPDX-License-Identifier: MIT
import re
from collections import defaultdict


class bcolors:
    PASS = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'


def num_systems(log):
    """
    Returns an integer of the number of systems that were tested during a
    particular run.
    """
    try:
        systems = re.findall(r'systems_\d+_', log)
        systems = re.findall(r'\d+', systems[0])
        return int(systems[0])
    except ValueError:
        return None


def _bobber_version(log):
    """
    Returns a string representation of the Bobber version tested, such as
    '2.7.1'. Raises a ValueError if the version cannot be parsed.
    """
    version = re.findall(r'version_\d+_\d+_\d+', log)
    if len(version) != 1:
        raise ValueError(f'Could not parse Bobber version from {log} file!')
    version = version[0].replace('version_', '')
    return version.replace('_', '.')


def check_bobber_version(logs, override):
    # Compare each new version with the previously captured version. If every
    # version matches the previous version seen, then all versions in a
    # directory are guaranteed to be the same.
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


def _convert_to_bytes(value):
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


def _fio_command_parse(command):
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


def _compare_dicts(old_results, new_results):
    """
    Compare the dictionaries for equality while ignoring the 'directory' and
    'command' keys since these fill always differ amongst tests.
    """
    ignore_keys = ['directory', 'command']

    old = dict((k, v) for k, v in old_results.items() if k not in ignore_keys)
    new = dict((k, v) for k, v in new_results.items() if k not in ignore_keys)
    return old == new


def fio_command_details(log_contents, old_reads, old_writes):
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
        else:
            raise ValueError('Unexpected FIO test type. Expected read/write.')
    if old_reads and old_writes:
        if not _compare_dicts(old_reads, read_params) or \
           not _compare_dicts(old_writes, write_params):
            raise ValueError('Parameters differ between tests. Ensure only '
                             'tests with the same parameters are used.')
    return read_params, write_params


def divide_logs_by_systems(log_files, log_to_match):
    # Divide the results based on the number of systems tested.
    num_systems_dict = defaultdict(list)

    for log in log_files:
        if log_to_match not in log:
            continue
        systems = num_systems(log)
        num_systems_dict[systems].append(log)
    return num_systems_dict
