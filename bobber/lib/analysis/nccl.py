# SPDX-License-Identifier: MIT
import re
from typing import Tuple


def parse_nccl_file(log_files: list, systems: int) -> Tuple[list, list]:
    """
    Find the maximum bus bandwidth and bus bytes from NCCL tests.

    Parse the bandwidth at all byte sizes achieved during NCCL tests and match
    the maximum bus bandwidth with the corresponding byte size from the
    results. Only the maximum and corresponding byte size from each log are
    returned to later find the overall average.

    Parameters
    ----------
    log_files : list
        A ``list`` of ``strings`` of the filenames for all NCCL log files in
        the results directory.
    systems : int
        An ``integer`` of the number of systems used during the current test.

    Returns
    -------
    tuple
        Returns a ``tuple`` of (``list``, ``list``) containing the maximum bus
        bandwidth and the bus bytes, respectively.
    """
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
