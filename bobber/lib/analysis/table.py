# SPDX-License-Identifier: MIT
import numpy as np
import operator
from bobber.lib.analysis.common import bcolors
from tabulate import tabulate


FIO_READ_BW = f'{bcolors.BOLD}FIO Read (GB/s) - 1MB BS{bcolors.ENDC}'
FIO_WRITE_BW = f'{bcolors.BOLD}FIO Write (GB/s) - 1MB BS{bcolors.ENDC}'
FIO_READ_IOP = f'{bcolors.BOLD}FIO Read (k IOPS) - 4K BS{bcolors.ENDC}'
FIO_WRITE_IOP = f'{bcolors.BOLD}FIO Write (k IOPS) - 4K BS{bcolors.ENDC}'
NCCL = f'{bcolors.BOLD}NCCL Max BW (GB/s){bcolors.ENDC}'
DALI_IMG_SM = (f'{bcolors.BOLD}DALI Standard 800x600 throughput '
               f'(images/second){bcolors.ENDC}')
DALI_IMG_SM_BW = (f'{bcolors.BOLD}DALI Standard 800x600 bandwidth '
                  f'(GB/s){bcolors.ENDC}')
DALI_IMG_LG = (f'{bcolors.BOLD}DALI Standard 3840x2160 throughput '
               f'(images/second){bcolors.ENDC}')
DALI_IMG_LG_BW = (f'{bcolors.BOLD}DALI Standard 3840x2160 bandwidth '
                  f'(GB/s){bcolors.ENDC}')
DALI_TF_SM = (f'{bcolors.BOLD}DALI TFRecord 800x600 throughput '
              f'(images/second){bcolors.ENDC}')
DALI_TF_SM_BW = (f'{bcolors.BOLD}DALI TFRecord 800x600 bandwidth '
                 f'(GB/s){bcolors.ENDC}')
DALI_TF_LG = (f'{bcolors.BOLD}DALI TFRecord 3840x2160 throughput '
              f'(images/second){bcolors.ENDC}')
DALI_TF_LG_BW = (f'{bcolors.BOLD}DALI TFRecord 3840x2160 bandwidth '
                 f'(GB/s){bcolors.ENDC}')


def bytes_to_gb(number):
    return round(number * 1e-9, 3)


def iops_to_kiops(number):
    return round(number * 1e-3, 3)


def scale(values):
    # Assuming scale is the calculated slope of the line of best fit divided by
    # the first value in the results, plus 1.
    x = np.array(range(1, len(values) + 1))
    y = np.array(values)
    slope, _ = np.polyfit(x, y, 1)
    return slope / values[0] + 1.0


def fio_bw(results):
    try:
        read = [FIO_READ_BW] + [bytes_to_gb(result[1]['bandwidth']['read'])
                                for result in results]
        write = [FIO_WRITE_BW] + [bytes_to_gb(result[1]['bandwidth']['write'])
                                  for result in results]
    except KeyError:
        return []
    else:
        return [read, write]


def fio_iops(results):
    try:
        read = [FIO_READ_IOP] + [iops_to_kiops(result[1]['iops']['read'])
                                 for result in results]
        write = [FIO_WRITE_IOP] + [iops_to_kiops(result[1]['iops']['write'])
                                   for result in results]
    except KeyError:
        return []
    else:
        return [read, write]


def nccl(results):
    try:
        nccl = [NCCL] + [round(result[1]['nccl']['max_bus_bw'], 3)
                         for result in results]
    except KeyError:
        return []
    else:
        return [nccl]


def dali(results):
    try:
        img_sm = [DALI_IMG_SM] + [result[1]['dali']['800x600 standard jpg']
                                  ['average images/second']
                                  for result in results]
        img_sm_bw = [DALI_IMG_SM_BW] + [bytes_to_gb(result[1]['dali']
                                                    ['800x600 standard jpg']
                                                    ['average bandwidth'])
                                        for result in results]
        img_lg = [DALI_IMG_LG] + [result[1]['dali']['3840x2160 standard jpg']
                                  ['average images/second']
                                  for result in results]
        img_lg_bw = [DALI_IMG_LG_BW] + [bytes_to_gb(result[1]['dali']
                                                    ['3840x2160 standard jpg']
                                                    ['average bandwidth'])
                                        for result in results]
        tf_sm = [DALI_TF_SM] + [result[1]['dali']['800x600 tfrecord']
                                ['average images/second']
                                for result in results]
        tf_sm_bw = [DALI_TF_SM_BW] + [bytes_to_gb(result[1]['dali']
                                                  ['800x600 tfrecord']
                                                  ['average bandwidth'])
                                      for result in results]
        tf_lg = [DALI_TF_LG] + [result[1]['dali']['3840x2160 tfrecord']
                                ['average images/second']
                                for result in results]
        tf_lg_bw = [DALI_TF_LG_BW] + [bytes_to_gb(result[1]['dali'][
                                                  '3840x2160 tfrecord']
                                                  ['average bandwidth'])
                                      for result in results]
    except KeyError:
        return []
    else:
        return [img_sm, img_sm_bw, img_lg, img_lg_bw, tf_sm, tf_sm_bw, tf_lg,
                tf_lg_bw]


def add_scale(data):
    for subset in data:
        # No results in the data - just the test category name
        if len(subset) < 2:
            continue
        # Scaling can't be calculated for NCCL as it has a different behavior
        # from other tests. For single-node only tests, there is nothing to
        # measure for scaling. Both scenarios should be ignored for calculating
        # scale factor.
        if 'nccl' in subset[0].lower() or len(subset) == 2:
            subset += ['N/A']
            continue
        values = subset[1:]
        scale_val = round(scale(values), 2)
        if scale_val > 1.9:
            scale_text = f'{bcolors.PASS}{scale_val}X{bcolors.ENDC}'
        elif scale_val > 1.5:
            scale_text = f'{bcolors.WARNING}{scale_val}X{bcolors.ENDC}'
        else:
            scale_text = f'{bcolors.FAIL}{scale_val}X{bcolors.ENDC}'
        subset += [scale_text]


def display_table(json_results):
    data = []
    headers = [f'{bcolors.BOLD}Test{bcolors.ENDC}'] + \
              [f'{bcolors.BOLD}{num} Node(s){bcolors.ENDC}'
               for num in sorted(json_results['systems'])] + \
              [f'{bcolors.BOLD}Scale{bcolors.ENDC}']
    results = sorted(json_results['systems'].items())

    data += fio_bw(results)
    data += fio_iops(results)
    data += nccl(results)
    data += dali(results)

    add_scale(data)

    print(tabulate(data, headers=headers, tablefmt='grid', numalign='right'))
    print()
