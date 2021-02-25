# SPDX-License-Identifier: MIT
import re
from bobber.lib.analysis.common import fio_command_details
from typing import Tuple


def clean_iops(iops: str) -> float:
    """
    Convert the IOPS into an equivalent operations/second result.

    Parse the IOPS value from the input string and convert the value from a
    larger unit to an equivalent operations/second, if applicable.

    Parameters
    ----------
    iops : str
        A ``string`` of the number of operations/second and resulting unit.

    Returns
    -------
    float
        Returns a ``float`` of the final IOPS value in operations/second.
    """
    number = float(re.findall(r'\d+', iops)[0])
    if 'G' in iops:
        ops_per_second = number * 1e9
    elif 'M' in iops:
        ops_per_second = number * 1e6
    elif 'k' in iops:
        ops_per_second = number * 1e3
    else:
        ops_per_second = number
    return ops_per_second


def clean_bw(bandwidth: str) -> float:
    """
    Convert the bandwidth into an equivalent bytes/second result.

    Parse the bandwidth value from the input string and convert the value from
    a larger unit to an equivalent operations/second, if applicable.

    Parameters
    ----------
    bandwidth : str
        A ``string`` of the bandwidth and unit from the test.

    Returns
    -------
    float
        Returns a ``float`` of the final bandwidth in bytes/second.
    """
    number = float(re.findall(r'(\d+(?:\.\d+)?)', bandwidth)[0])
    if 'GB/s' in bandwidth:
        bytes_per_second = number * 1e9
    elif 'MB/s' in bandwidth:
        bytes_per_second = number * 1e6
    elif 'kb/s' in bandwidth.lower():
        bytes_per_second = number * 1e3
    else:
        bytes_per_second = number
    return bytes_per_second


def fio_bw_results(log_contents: str, systems: int, string_to_match: str,
                   log: str) -> list:
    """
    Capture the bandwidth results from the log files.

    Search the log for any lines containing a bandwidth value and return a
    final list of all of the parsed values.

    Parameters
    ----------
    log_contents : str
        A ``string`` of the contents from an FIO log file.
    systems : int
        An ``integer`` of the number of systems used during the current test.
    string_to_match : str
        A regex ``string`` of the line to pull from the log file to match any
        bandwidth lines.
    log : str
        A ``string`` of the name of the log file being parsed.

    Returns
    -------
    list
        Returns a ``list`` of ``floats`` representing all of the bandwidth
        values parsed from the log.

    Raises
    ------
    ValueError
        Raises a ``ValueError`` if the bandwidth cannot be parsed from the log
        file.
    """
    final_bw = []

    match = re.findall(string_to_match, log_contents)
    if len(match) != systems:
        print(f'Warning: Invalid number of results found in {log} log file. '
              'Skipping...')
        return []
    for result in match:
        bw = re.findall(r'\(\d+[kMG]B/s\)', result)
        if len(bw) != 1:
            bw = re.findall(r'\(\d+\.\d+[kMG]B/s\)', result)
            if len(bw) != 1:
                raise ValueError('Bandwidth cannot be parsed from FIO log!')
        bw = clean_bw(bw[0])
        final_bw.append(bw)
    return final_bw


def fio_iops_results(log_contents: str, systems: int, string_to_match: str,
                     log: str) -> list:
    """
    Capture the IOPS results from the log files.

    Search the log for any lines containing IOPS values and return a final list
    of all of the parsed values. The FIO IOPS tests print an extra line for
    multi-node tests and are subsequently dropped.

    Parameters
    ----------
    log_contents : str
        A ``string`` of the contents from an FIO log file.
    systems : int
        An ``integer`` of the number of systems used during the current test.
    string_to_match : str
        A regex ``string`` of the line to pull from the log file to match any
        IOPS lines.
    log : str
        A ``string`` of the name of the log file being parsed.

    Returns
    -------
    list
        Returns a ``list`` of ``floats`` representing all of the IOPS values
        parsed from the log.

    Raises
    ------
    ValueError
        Raises a ``ValueError`` if the IOPS cannot be parsed from the log
        file.
    """
    final_iops = []

    match = re.findall(string_to_match, log_contents)
    if (systems == 1 and len(match) != systems) or \
       (systems != 1 and len(match) != systems + 1):
        print(f'Warning: Invalid number of results found in {log} log file. '
              'Skipping...')
        return []
    for result in match:
        iops = re.findall(r'[-+]?\d*\.\d+[kMG]|\d+[kMG]|\d+', result)
        if len(iops) != 5:
            raise ValueError('IOPS cannot be parsed from FIO log!')
        iops = clean_iops(iops[0])
        final_iops.append(iops)
    # For multi-system benchmarks, an extra IOPS line is included with
    # semi-aggregate results, but needs to be dropped from our results for a
    # more accurate analysis.
    if systems != 1:
        final_iops = final_iops[:-1]
    return final_iops


def parse_fio_bw_file(log_files: list, systems: int, read_system_results: dict,
                      write_system_results: dict) -> Tuple[dict, dict, dict,
                                                           dict]:
    """
    Parse the FIO bandwidth results and test parameters.

    Search all log files for read and write parameters used to initiate the
    test and the final results and return the resulting objects.

    Parameters
    ----------
    log_files : list
        A ``list`` of ``strings`` of the filenames of all FIO bandwidth logs in
        the results directory.
    systems : int
        An ``integer`` of the number of systems used during the current test.
    read_system_results : dict
        A ``dictionary`` of the final read results for N-systems.
    write_system_results : dict
        A ``dictionary`` of the final write results for N-systems.

    Returns
    -------
    tuple
        A ``tuple`` of four dictionaries containing the read results, write
        results, read parameters, and write parameters, respectively.
    """
    read_params, write_params = None, None

    for log in log_files:
        with open(log, 'r') as f:
            log_contents = f.read()
        read_params, write_params = fio_command_details(log_contents,
                                                        read_params,
                                                        write_params)
        write_bw = fio_bw_results(log_contents, systems, 'WRITE: bw=.*', log)
        if write_bw == []:
            continue
        read_bw = fio_bw_results(log_contents, systems, 'READ: bw=.*', log)
        write_system_results[systems].append(sum(write_bw))
        read_system_results[systems].append(sum(read_bw))
    return read_system_results, write_system_results, read_params, write_params


def parse_fio_iops_file(log_files: list, systems: int,
                        read_system_results: dict,
                        write_system_results: dict) -> Tuple[dict, dict, dict,
                                                             dict]:
    """
    Parse the FIO IOPS results and test parameters.

    Search all log files for read and write parameters used to initiate the
    test and the final results and return the resulting objects.

    Parameters
    ----------
    log_files : list
        A ``list`` of ``strings`` of the filenames of all FIO IOPS logs in the
        results directory.
    systems : int
        An ``integer`` of the number of systems used during the current test.
    read_system_results : dict
        A ``dictionary`` of the final read results for N-systems.
    write_system_results : dict
        A ``dictionary`` of the final write results for N-systems.

    Returns
    -------
    tuple
        A ``tuple`` of four dictionaries containing the read results, write
        results, read parameters, and write parameters, respectively.
    """
    read_params, write_params = None, None

    for log in log_files:
        with open(log, 'r') as f:
            log_contents = f.read()
        read_params, write_params = fio_command_details(log_contents,
                                                        read_params,
                                                        write_params)
        write_iops = fio_iops_results(log_contents, systems, 'write: IOPS=.*',
                                      log)
        read_iops = fio_iops_results(log_contents, systems, 'read: IOPS=.*',
                                     log)
        write_system_results[systems].append(sum(write_iops))
        read_system_results[systems].append(sum(read_iops))
    return read_system_results, write_system_results, read_params, write_params
