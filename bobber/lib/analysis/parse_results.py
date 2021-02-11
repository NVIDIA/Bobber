# SPDX-License-Identifier: MIT
import json
import sys
from collections import defaultdict
from datetime import datetime
from glob import glob
from os.path import join
from bobber.lib.analysis.aggregate_results import AggregateResults
from bobber.lib.analysis.common import (check_bobber_version,
                                        divide_logs_by_systems)
from bobber.lib.analysis.compare_baseline import compare_baseline
from bobber.lib.analysis.dali import parse_dali_file
from bobber.lib.analysis.fio import parse_fio_bw_file, parse_fio_iops_file
from bobber.lib.analysis.nccl import parse_nccl_file
from bobber.lib.analysis.table import display_table


def get_files(directory):
    return glob(join(directory, '*.log'))


def parse_fio_bw(log_files):
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


def parse_fio_iops(log_files):
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


def parse_nccl(log_files):
    bw_results = defaultdict(list)
    bytes_results = defaultdict(list)

    nccl_logs_by_systems = divide_logs_by_systems(log_files, 'nccl')

    for systems, files in nccl_logs_by_systems.items():
        max_bw, byte_size = parse_nccl_file(files, systems)
        bw_results[systems] = max_bw
        bytes_results[systems] = byte_size
    return bw_results, bytes_results


def parse_dali(log_files):
    results_dict = {}

    dali_logs_by_systems = divide_logs_by_systems(log_files, 'dali')

    for systems, files in dali_logs_by_systems.items():
        results_dict = parse_dali_file(files, systems, results_dict)
    return results_dict


def verify_template(template):
    print('Analyzing the template file for accuracy...')
    print()
    print(template)
    prompt = 'Are the above details accurate based on the passed logs? [y/n]: '

    while True:
        try:
            response = input(prompt)
        except KeyboardInterrupt:
            print('Keyboard interrupt - exiting...')
            sys.exit()
        if response.lower().strip() == 'y':
            break
        elif response.lower().strip() == 'n':
            print()
            print('Please update the template file located in '
                  'analysis/template.yaml and run again.')
            print('Exiting...')
            sys.exit()


def save_json(final_dictionary_output, filename):
    if not filename:
        stamp = datetime.now()
        filename = (f'bobber_results_{stamp.date()}_{stamp.hour}.'
                    f'{stamp.minute}.{stamp.second}.json')
    with open(filename, 'w') as json_file:
        json.dump(final_dictionary_output, json_file)
        print(f'JSON data saved to {filename}')


def main(directory, baseline=None, custom_baseline=None, tolerance=0,
         verbose=False, override_version_check=False, json_filename=None):
    final_dictionary_output = {'systems': {}}

    log_files = get_files(directory)
    bobber_version = check_bobber_version(log_files,
                                          override_version_check)
    bw_results = parse_fio_bw(log_files)
    read_bw, write_bw, read_bw_params, write_bw_params = bw_results
    iops_results = parse_fio_iops(log_files)
    read_iops, write_iops, read_iops_params, write_iops_params = iops_results
    max_bw, bytes_sizes = parse_nccl(log_files)
    dali_results = parse_dali(log_files)
    total_systems = 0
    systems = []

    for result in [read_bw, read_iops, max_bw, dali_results]:
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
                                     max_bw,
                                     bytes_sizes,
                                     dali_results,
                                     system_num)
        final_dictionary_output['systems'][str(system_num)] = aggregate.json
        if verbose:
            print(aggregate)

    final_dictionary_output['total_systems'] = total_systems
    final_dictionary_output['bobber_version'] = bobber_version
    display_table(final_dictionary_output)
    save_json(final_dictionary_output, json_filename)

    if custom_baseline:
        compare_baseline(final_dictionary_output, custom_baseline, tolerance,
                         custom=True)
    elif baseline:
        compare_baseline(final_dictionary_output, baseline, tolerance)
