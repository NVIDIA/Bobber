# SPDX-License-Identifier: MIT
import re


def parse_nccl_file(log_files, systems):
    max_bus_bw_list = []
    bus_bytes_list = []

    for log in log_files:
        with open(log, 'r') as f:
            log_contents = f.read()
        out_of_place_results = re.findall('.*float     sum.*', log_contents)
        results = [line.split() for line in out_of_place_results]
        bytes_array = [float(result[0]) for result in results]
        bus_bw_array = [float(result[6]) for result in results]
        max_bus_bw_list.append(max(bus_bw_array))
        max_index = bus_bw_array.index(max(bus_bw_array))
        bus_bytes_list.append(bytes_array[max_index])
    return max_bus_bw_list, bus_bytes_list
