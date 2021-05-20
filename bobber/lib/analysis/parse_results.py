# SPDX-License-Identifier: MIT
import json
import sys
from collections import defaultdict
from glob import glob
from os.path import join
from bobber.lib.exit_codes import MISSING_LOG_FILES, SUCCESS
from bobber.lib.analysis.aggregate_results import AggregateResults
from bobber.lib.analysis.common import (check_bobber_version,
                                        divide_logs_by_systems)
from bobber.lib.analysis.compare_baseline import compare_baseline
from bobber.lib.analysis.dali import parse_dali_file
from bobber.lib.analysis.fio import parse_fio_bw_file, parse_fio_iops_file
from bobber.lib.analysis.meta import parse_meta_file
from bobber.lib.analysis.nccl import parse_nccl_file
from bobber.lib.analysis.table import display_table
from bobber.lib.system.file_handler import write_file
from typing import NoReturn, Optional, Tuple


def get_files(directory: str) -> list:
    """
    Read all log files.

    Given an input directory as a string, read all log files and return the
    filenames including the directory as a list.

    Parameters
    ----------
    directory : str
        A ``string`` pointing to the results directory.

    Returns
    -------
    list
        Returns a ``list`` of ``strings`` of the paths to each log file in the
        results directory.
    """
    return glob(join(directory, '*.log'))


def parse_fio_bw(log_files: list) -> Tuple[dict, dict, dict, dict]:
    """
    Parse all FIO bandwidth logs.

    Find each FIO bandwidth log in the results directory and parse the read and
    write results and parameters from each log for all system counts.

    Parameters
    ----------
    log_files : list
        A ``list`` of ``strings`` of the paths to each log file in the results
        directory.

    Returns
    -------
    tuple
        A ``tuple`` of four dictionaries containing the read results, write
        results, read parameters, and write parameters, respectively for all
        system counts.
    """
    read_sys_results = defaultdict(list)
    write_sys_results = defaultdict(list)
    read_params, write_params = None, None

    fio_logs_by_systems = divide_logs_by_systems(log_files, 'stg_bw_iteration')

    for systems, files in fio_logs_by_systems.items():
        read_sys_results, write_sys_results, read_params, write_params = \
            parse_fio_bw_file(files,
                              systems,
                              read_sys_results,
                              write_sys_results)
    return read_sys_results, write_sys_results, read_params, write_params


def parse_fio_iops(log_files: list) -> Tuple[dict, dict, dict, dict]:
    """
    Parse all FIO IOPS logs.

    Find each FIO IOPS log in the results directory and parse the read and
    write results and parameters from each log for all system counts.

    Parameters
    ----------
    log_files : list
        A ``list`` of ``strings`` of the paths to each log file in the results
        directory.

    Returns
    -------
    tuple
        A ``tuple`` of four dictionaries containing the read results, write
        results, read parameters, and write parameters, respectively for all
        system counts.
    """
    read_sys_results = defaultdict(list)
    write_sys_results = defaultdict(list)
    read_params, write_params = None, None

    fio_logs_by_systems = divide_logs_by_systems(log_files,
                                                 'stg_iops_iteration')

    for systems, files in fio_logs_by_systems.items():
        read_sys_results, write_sys_results, read_params, write_params = \
            parse_fio_iops_file(files,
                                systems,
                                read_sys_results,
                                write_sys_results)
    return read_sys_results, write_sys_results, read_params, write_params


def parse_fio_125k_bw(log_files: list) -> Tuple[dict, dict, dict, dict]:
    """
    Parse all FIO 125k bandwidth logs.

    Find each FIO 125k bandwidth log in the results directory and parse the
    read and write results and parameters from each log for all system counts.

    Parameters
    ----------
    log_files : list
        A ``list`` of ``strings`` of the paths to each log file in the results
        directory.

    Returns
    -------
    tuple
        A ``tuple`` of four dictionaries containing the 125k read results, 125k
        write results, 125k read parameters, and 125k write parameters for all
        system counts.
    """
    read_sys_results = defaultdict(list)
    write_sys_results = defaultdict(list)
    read_params, write_params = None, None

    fio_logs_by_systems = divide_logs_by_systems(log_files,
                                                 'stg_125k_iteration')

    for systems, files in fio_logs_by_systems.items():
        read_sys_results, write_sys_results, read_params, write_params = \
            parse_fio_bw_file(files,
                              systems,
                              read_sys_results,
                              write_sys_results)
    return read_sys_results, write_sys_results, read_params, write_params


def parse_nccl(log_files: list) -> Tuple[dict, dict]:
    """
    Parse all NCCL logs.

    Find the maximum bus bandwidth and resulting byte size for all NCCL files
    for all system counts.

    Parameters
    ----------
    log_files : list
        A ``list`` of ``strings`` of the paths to each log file in the results
        directory.

    Returns
    -------
    tuple
        Returns a ``tuple`` of (``dict``, ``dict``) representing the maximum
        bus bandwidth and corresponding byte size for all system counts.
    """
    bw_results = defaultdict(list)
    bytes_results = defaultdict(list)

    nccl_logs_by_systems = divide_logs_by_systems(log_files, 'nccl')

    for systems, files in nccl_logs_by_systems.items():
        max_bw, byte_size = parse_nccl_file(files, systems)
        bw_results[systems] = max_bw
        bytes_results[systems] = byte_size
    return bw_results, bytes_results


def parse_dali(log_files: list) -> dict:
    """
    Parse all DALI logs.

    Parse the bandwidth and throughput for all image types and sizes from all
    DALI log files.

    Parameters
    ----------
    log_files : list
        A ``list`` of ``strings`` of the paths to each log file in the results
        directory.

    Returns
    -------
    dict
        Returns a ``dictionary`` of the throughput and bandwidth for all system
        counts.
    """
    results_dict = {}

    dali_logs_by_systems = divide_logs_by_systems(log_files, 'dali')

    for systems, files in dali_logs_by_systems.items():
        results_dict = parse_dali_file(files, systems, results_dict)
    return results_dict


def parse_meta(log_files: list) -> dict:
    """
    Parse all metadata logs.

    Parse the minimum, maximum, and mean values for all operations in the
    metadata log files.

    Parameters
    ----------
    log_files : list
        A ``list`` of ``strings`` of the paths to each log file in the results
        directory.

    Returns
    -------
    dict
        Returns a ``dictionary`` of the results from various metadata
        operations for all system counts.
    """
    results_dict = {}

    meta_logs_by_systems = divide_logs_by_systems(log_files, 'stg_meta')

    for systems, files in meta_logs_by_systems.items():
        results_dict = parse_meta_file(files, systems, results_dict)
    return results_dict


def save_json(final_dictionary_output: dict, filename: str) -> NoReturn:
    """
    Save results to a file.

    Save the final JSON data to a file for future reference. If the filename is
    not specified, don't save the file.

    Parameters
    ----------
    final_dictionary_output : dict
        A ``dictionary`` of the final JSON output to save.
    filename : str
        A ``string`` of the filename to write the JSON data to.
    """
    if not filename:
        return
    with open(filename, 'w') as json_file:
        json.dump(final_dictionary_output, json_file)
        print(f'JSON data saved to {filename}')


def save_yaml_baseline(final_dictionary_output: dict,
                       directory: str) -> NoReturn:
    """
    Save results as a YAML baseline file.

    The parsed results should be saved as a YAML baseline file which can be
    used to compare similar systems against existing results. The YAML file
    will be saved in the results directory as "baseline.yaml".

    Parameters
    ----------
    final_dictionary_output : dict
        A ``dictionary`` of the parsed results on a per-system level.
    directory : str
        A ``string`` of the directory where results are saved.
    """
    contents = 'systems:\n'

    for systems, results in final_dictionary_output['systems'].items():
        dali = results.get('dali', {})
        small_jpg = dali.get('800x600 standard jpg', {})
        large_jpg = dali.get('3840x2160 standard jpg', {})
        small_tf = dali.get('800x600 tfrecord', {})
        large_tf = dali.get('3840x2160 tfrecord', {})
        contents += f"""    {systems}:
        bandwidth:
            # FIO BW speed in bytes/second
            read: {results.get('bandwidth', {}).get('read', 0)}
            write: {results.get('bandwidth', {}).get('write', 0)}
        iops:
            # FIO IOPS speed in ops/second
            read: {results.get('iops', {}).get('read', 0)}
            write: {results.get('iops', {}).get('write', 0)}
        125k_bandwidth:
            # FIO 125k BW speed in bytes/second
            read: {results.get('125k_bandwidth', {}).get('read', 0)}
            write: {results.get('125k_bandwidth', {}).get('write', 0)}
        nccl:
            # NCCL maximum bus bandwidth in GB/s
            max_bus_bw: {results.get('nccl', {}).get('max_bus_bw', 0)}
        dali:
            # DALI average speed in images/second
            800x600 standard jpg: {small_jpg.get('average images/second', 0)}
            3840x2160 standard jpg: {large_jpg.get('average images/second', 0)}
            800x600 tfrecord: {small_tf.get('average images/second', 0)}
            3840x2160 tfrecord: {large_tf.get('average images/second', 0)}
"""
    write_file(f'{directory}/baseline.yaml', contents)


def main(directory: str,
         baseline: Optional[str] = None,
         custom_baseline: Optional[str] = None,
         tolerance: Optional[int] = 0,
         verbose: Optional[bool] = False,
         override_version_check: Optional[bool] = False,
         json_filename: Optional[str] = None) -> NoReturn:
    """
    Parse all results on a per-system level.

    Read all log files from a results directory and iterate through the results
    on a per-system level. The results displayed are of the aggregate value for
    each system count.

    A baseline can be optionally included to compare the results in the output
    directory against pre-configured results to verify performance meets
    desired levels.

    Parameters
    ----------
    directory : str
        A ``string`` of the directory where results are located.
    baseline : str (optional)
        A ``string`` representing the key from the included baselines to
        compare results to.
    custom_baseline : str (optional)
        A ``string`` of the filename to a custom YAML config file to read and
        compare results to.
    tolerance : int (optional)
        An ``integer`` of the tolerance as a percentage below the baseline to
        allow results to still be marked as passing.
    verbose : bool (optional)
        A ``boolean`` that prints additional textual output when `True`.
    override_version_check : bool (optional)
        A ``boolean`` which skips checking the Bobber version tested when
        `True`.
    json_filename : str (optional)
        A ``string`` of the filename to save JSON data to.
    """
    final_dictionary_output = {'systems': {}}

    log_files = get_files(directory)
    if len(log_files) < 1:
        print('No log files found. Please specify a directory containing '
              'valid logs.')
        print('Exiting...')
        sys.exit(MISSING_LOG_FILES)
    bobber_version = check_bobber_version(log_files,
                                          override_version_check)
    bw_results = parse_fio_bw(log_files)
    read_bw, write_bw, read_bw_params, write_bw_params = bw_results
    bw_125k_results = parse_fio_125k_bw(log_files)
    read_125k_bw, write_125k_bw, read_125k_bw_params, write_125k_bw_params = \
        bw_125k_results
    iops_results = parse_fio_iops(log_files)
    read_iops, write_iops, read_iops_params, write_iops_params = iops_results
    metadata = parse_meta(log_files)
    max_bw, bytes_sizes = parse_nccl(log_files)
    dali_results = parse_dali(log_files)
    total_systems = 0
    systems = []

    for result in [read_bw, read_iops, read_125k_bw, max_bw, dali_results,
                   metadata]:
        try:
            total_systems = max(result.keys())
            systems = sorted(result.keys())
        except ValueError:
            continue
        else:
            break

    for system_num in systems:
        aggregate = AggregateResults(read_bw,
                                     write_bw,
                                     read_bw_params,
                                     write_bw_params,
                                     read_iops,
                                     write_iops,
                                     read_iops_params,
                                     write_iops_params,
                                     read_125k_bw,
                                     write_125k_bw,
                                     read_125k_bw_params,
                                     write_125k_bw_params,
                                     max_bw,
                                     bytes_sizes,
                                     dali_results,
                                     metadata,
                                     system_num)
        final_dictionary_output['systems'][str(system_num)] = aggregate.json
        if verbose:
            print(aggregate)

    final_dictionary_output['total_systems'] = total_systems
    final_dictionary_output['bobber_version'] = bobber_version
    display_table(final_dictionary_output)
    save_yaml_baseline(final_dictionary_output, directory)
    save_json(final_dictionary_output, json_filename)

    if custom_baseline:
        compare_baseline(final_dictionary_output, custom_baseline, tolerance,
                         custom=True)
    elif baseline:
        compare_baseline(final_dictionary_output, baseline, tolerance)
