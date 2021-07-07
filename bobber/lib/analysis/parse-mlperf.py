# SPDX-License-Identifier: MIT
import re
from argparse import ArgumentParser, Namespace
from glob import glob
from os.path import join
from typing import NoReturn, Tuple


class Aggregate:
    """
    Find the aggregate results for from multiple iterations.

    Parameters
    ----------
    epoch_zero_speeds : list
        A ``list`` of ``floats`` of the first epoch speeds.
    epoch_zero_times : list
        A ``list`` of ``floats`` of the epoch zero times.
    elapsed_times : list
        A ``list`` of ``floats`` of the overall elapsed time.
    average_speeds : list
        A ``list`` of ``floats`` of the overall average speeds.
    """
    def __init__(self, epoch_zero_speeds: list, epoch_zero_times: list,
                 elapsed_times: list, average_speeds: list) -> NoReturn:
        self.epoch_zero_speeds = epoch_zero_speeds
        self.epoch_zero_times = epoch_zero_times
        self.elapsed_times = elapsed_times
        self.average_speeds = average_speeds


class Results:
    """
    The results from a single test run.

    Parameters
    ----------
    epoch_zero_speed : float
        A ``float`` of the first epoch speed.
    epoch_zero_time : float
        A ``float`` of the epoch zero time.
    elapsed_time : float
        A ``float`` of the overall elapsed time.
    average_speed : float
        A ``float`` of the overall average speed.
    """
    def __init__(self, epoch_zero_speed: float, epoch_zero_time: float,
                 elapsed_time: float, average_speed: float) -> NoReturn:
        self.epoch_zero_speed = epoch_zero_speed
        self.epoch_zero_time = epoch_zero_time
        self.elapsed_time = elapsed_time
        self.average_speed = average_speed


def parse_args() -> Namespace:
    """
    Parse arguments passed to the MLPerf parser.

    Returns
    -------
    Namespace
        Returns a ``Namespace`` of all of the arguments that were parsed from
        the application during runtime.
    """
    parser = ArgumentParser(description='Parse MLPerf results')
    parser.add_argument('directory', type=str, help='The directory where '
                        'MLPerf log results are saved.')
    return parser.parse_args()


def average(list_to_average: list) -> float:
    """
    Find the average of a list.

    Given a list of numbers, calculate the average of all values in the list.
    If the list is empty, default to 0.0.

    Parameters
    ----------
    list_to_average : list
        A ``list`` of ``floats`` to find an average of.

    Returns
    -------
    float
        Returns a ``float`` of the average value of the list.
    """
    try:
        return round(sum(list_to_average) / len(list_to_average), 3)
    except ZeroDivisionError:
        return 0.0


def ms_to_seconds(time: float) -> float:
    """
    Convert milliseconds to seconds.

    Parameters
    ----------
    time : float
        A ``float`` of time in milliseconds.

    Returns
    -------
    float
        Returns a ``float`` of the converted time in seconds.
    """
    return round(time / 1000, 3)


def ms_to_minutes(time: float) -> float:
    """
    Convert milliseconds to minutes.

    Parameters
    ----------
    time : float
        A ``float`` of time in milliseconds.

    Returns
    -------
    float
        Returns a ``float`` of the converted time in minutes.
    """
    return round(time / 1000 / 60, 3)


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


def parse_epoch_line(line: str) -> Tuple[int, float]:
    """
    Parse the throughput for each epoch.

    Pull the images/second and epoch for each results line in an MLPerf log.

    Parameters
    ----------
    line : str
        A ``string`` of a results line in an MLPerf log.

    Returns
    -------
    tuple
        Returns a ``tuple`` of (``int``, ``float``) of the epoch number and
        resulting speed in images/second.
    """
    # Lines are in the format:
    # "Epoch[NUM] Batch [NUM-NUM] Speed: NUM.NUM samples/sec accuracy=NUM.NUM"
    epoch = re.findall(r'\[\d+\]', line)[0].replace('[', '').replace(']', '')
    speed = re.findall(r'Speed: .* samples', line)
    if len(speed) == 1:
        speed = speed[0].replace('Speed: ', '').replace(' samples', '')
    return int(epoch), float(speed)


def parse_time(line: str) -> int:
    """
    Parse the timestamp from a line in the log.

    Parameters
    ----------
    line : str
        A ``string`` of a line in an MLPerf log file.

    Returns
    -------
    int
        Returns an ``int`` of the parsed timestamp.
    """
    return int(re.findall(r'\d+', line)[0])


def parse_epoch_values(logfile: str) -> Tuple[list, list]:
    """
    Parse the epoch and throughput lines.

    Find all of the lines that contain a throughput and save the first epoch
    and overall epoch results in lists.

    Parameters
    ----------
    logfile : str
        A ``string`` of all contents from a logfile.

    Returns
    -------
    tuple
        Returns a ``tuple`` of (``list``, ``list``) containing the first epoch
        results followed by all results.
    """
    epoch_zero_vals, all_epoch_vals = [], []
    epoch_values = re.findall(r'Epoch\[\d+\] Batch.*', logfile)

    for value in epoch_values:
        epoch, speed = parse_epoch_line(value)
        all_epoch_vals.append(speed)
        if epoch == 0:
            epoch_zero_vals.append(speed)
    return epoch_zero_vals, all_epoch_vals


def parse_epoch_times(logfile: str) -> Tuple[list, list]:
    """
    Parse the time for each epoch.

    Find the overall time it takes to complete each epoch by finding the
    difference in milliseconds.

    Parameters
    ----------
    logfile : str
        A ``string`` of all contents from a logfile.

    Returns
    -------
    tuple
        Returns a ``tuple`` of (``list``, ``list``) representing the time taken
        during the first epoch and the overall elapsed time for the test.
    """
    epoch_start_times = re.findall(r'time_ms.*?epoch_start', logfile)
    epoch_stop_times = re.findall(r'time_ms.*?epoch_stop', logfile)
    # The epoch 0 time is the difference between the timestamp where epoch 0
    # ended, and the timestamp where epoch 0 began.
    epoch_zero_time = parse_time(epoch_stop_times[0]) - \
        parse_time(epoch_start_times[0])
    # The total elapsed time is the difference between the timestamp of when
    # the final epoch ended, and the timestamp where epoch 0 began.
    elapsed_time = parse_time(epoch_stop_times[-1]) - \
        parse_time(epoch_start_times[0])
    return epoch_zero_time, elapsed_time


def parse_file(logfile: str) -> object:
    """
    Parse a single MLPerf file.

    Find the first epoch and overall results for a single MLPerf file and
    create a singular object to represent the results.

    Parameters
    ----------
    logfile : str
        A ``string`` of all contents from a logfile.

    Returns
    -------
    Results instance
        Returns an instance of the Results class.
    """
    epoch_zero_vals, all_epoch_vals = parse_epoch_values(logfile)
    epoch_zero_time, elapsed_time = parse_epoch_times(logfile)
    results = Results(average(epoch_zero_vals),
                      epoch_zero_time,
                      elapsed_time,
                      average(all_epoch_vals))
    return results


def find_num_nodes(logfile: str) -> int:
    """
    Find the number of nodes tested.

    Parameters
    ----------
    logfile : str
        A ``string`` of all contents from a logfile.

    Returns
    -------
    int
        Returns an ``integer`` of the number of nodes tested.
    """
    clear_cache_command = re.findall(r'srun.*Clearing cache on ', logfile)
    if len(clear_cache_command) == 0:
        print('Unable to find number of nodes tested. Assuming single node.')
        return 1
    n_tasks = re.findall(r'ntasks=\d+', clear_cache_command[0])
    num_nodes = n_tasks[0].replace('ntasks=', '')
    return num_nodes


def find_filesystem_test_path(logfile: str) -> str:
    """
    Parse the filesystem path from the log file.

    The 'container-mounts=...' line in each log file contains the location of
    the shared filesystem.

    Parameters
    ----------
    logfiles : str
        A ``string`` of all contents from a logfile.

    Returns
    -------
    str
        Returns a ``string`` of the location of the filesystem.
    """
    container_mounts_line = re.findall(r'container-mounts=\S*:/data', logfile)
    if len(container_mounts_line) == 0:
        print('Unable to find container mount directory. Leaving empty.')
        return '<Unknown>'
    container_data_mount = container_mounts_line[0].replace(
        'container-mounts=', '')
    return container_data_mount


def read_files(logfiles: list) -> Tuple[object, int, str]:
    """
    Read all MLPerf files and find aggregate results.

    Read all log files in a directory and determine the average speed and time
    taken to process images for both the first epoch and all results combined.

    Parameters
    ----------
    logfiles : list
        A ``list`` of the filepaths for all log files in an input directory.

    Returns
    -------
    tuple
        Returns a ``tuple`` of an instance of the Aggregate class, the number
        of nodes tested, and the path to the filesystem under test.
    """
    all_results = []
    prev_nodes_found = None
    prev_filesystem_test_path = None

    for filename in logfiles:
        with open(filename, 'r') as logpointer:
            log = logpointer.read()
            results = parse_file(log)
            all_results.append(results)
            nodes_tested = find_num_nodes(log)
            filesystem_test_path = find_filesystem_test_path(log)
            if prev_nodes_found and nodes_tested != prev_nodes_found:
                raise ValueError('Error: Mixed node sizes found in log files!')
            if prev_filesystem_test_path and \
                    filesystem_test_path != prev_filesystem_test_path:
                raise ValueError('Error: Mixed test paths found in log files!')
            prev_nodes_found = nodes_tested
            prev_filesystem_test_path = filesystem_test_path
    aggregate = Aggregate(
        [result.epoch_zero_speed for result in all_results],
        [result.epoch_zero_time for result in all_results],
        [result.elapsed_time for result in all_results],
        [result.average_speed for result in all_results]
    )
    return aggregate, nodes_tested, filesystem_test_path


def print_averages(results: object, directory: str, nodes_tested: int,
                   filesystem_test_path: str) -> NoReturn:
    """
    Print the average results.

    Print the average time and speed for epoch 0 and all results, plus test
    information including the log directory and the location of the filesystem
    under test.

    Parameters
    ----------
    results : object
        An instance of the Results class containing the results from a single
        test.
    directory : str
        A ``string`` of the passed directory where results were saved.
    nodes_tested : int
        An ``int`` of the number of nodes that were tested for a file.
    filesystem_test_path : str
        A ``string`` of the path to the filesystem under test.
    """
    e_zero_speed = average(results.epoch_zero_speeds)
    e_zero_time = ms_to_seconds(average(results.epoch_zero_times))
    overall_speed = average(results.average_speeds)
    overall_time = ms_to_minutes(average(results.elapsed_times))

    output = f"""MLPerf Results:
Log directory name: {directory}
Filesystem test path: {filesystem_test_path}
Number of iterations: {len(results.epoch_zero_speeds)}
Nodes tested: {nodes_tested}
Epoch 0:
    Speed: {e_zero_speed} images/second
    Average time: {e_zero_time} seconds
Overall:
    Speed: {overall_speed} images/second
    Average time: {overall_time} minutes"""
    print(output)


def main() -> NoReturn:
    """
    Parse MLPerf test results.
    """
    args = parse_args()
    logfiles = get_files(args.directory)
    aggregate, nodes_tested, filesystem_test_path = read_files(logfiles)
    print_averages(aggregate, args.directory, nodes_tested,
                   filesystem_test_path)


if __name__ == '__main__':
    main()
