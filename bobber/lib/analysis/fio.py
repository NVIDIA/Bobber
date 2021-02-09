# SPDX-License-Identifier: MIT
import re
from bobber.lib.analysis.common import fio_command_details


def clean_iops(iops):
    # Convert the IOPS into an equivalent operations/second result.
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


def clean_bw(bandwidth):
    # Convert the bandwidth into an equivalent bytes/second result.
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


def fio_bw_results(log_contents, systems, string_to_match, log):
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


def fio_iops_results(log_contents, systems, string_to_match, log):
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


def parse_fio_bw_file(log_files, systems, read_system_results,
                      write_system_results):
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


def parse_fio_iops_file(log_files, systems, read_system_results,
                        write_system_results):
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
