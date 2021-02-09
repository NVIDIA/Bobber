# SPDX-License-Identifier: MIT
import re
from argparse import ArgumentParser
from glob import glob
from os.path import join


class Aggregate:
    def __init__(self, epoch_zero_speeds, epoch_zero_times, elapsed_times,
                 average_speeds):
        self.epoch_zero_speeds = epoch_zero_speeds
        self.epoch_zero_times = epoch_zero_times
        self.elapsed_times = elapsed_times
        self.average_speeds = average_speeds


class Results:
    def __init__(self, epoch_zero_speed, epoch_zero_time, elapsed_time,
                 average_speed):
        self.epoch_zero_speed = epoch_zero_speed
        self.epoch_zero_time = epoch_zero_time
        self.elapsed_time = elapsed_time
        self.average_speed = average_speed


def parse_args():
    parser = ArgumentParser(description='Parse MLPerf results')
    parser.add_argument('directory', type=str, help='The directory where '
                        'MLPerf log results are saved.')
    return parser.parse_args()


def average(list_to_average):
    try:
        return round(sum(list_to_average) / len(list_to_average), 3)
    except ZeroDivisionError:
        return 0.0


def ms_to_seconds(time):
    return round(time / 1000, 3)


def ms_to_minutes(time):
    return round(time / 1000 / 60, 3)


def get_files(directory):
    return glob(join(directory, '*.log'))


def parse_epoch_line(line):
    # Lines are in the format:
    # "Epoch[NUM] Batch [NUM-NUM] Speed: NUM.NUM samples/sec accuracy=NUM.NUM"
    epoch = re.findall(r'\[\d+\]', line)[0].replace('[', '').replace(']', '')
    speed = re.findall(r'Speed: .* samples', line)
    if len(speed) == 1:
        speed = speed[0].replace('Speed: ', '').replace(' samples', '')
    return int(epoch), float(speed)


def parse_time(line):
    return int(re.findall(r'\d+', line)[0])


def parse_epoch_values(logfile):
    epoch_zero_vals, all_epoch_vals = [], []
    epoch_values = re.findall(r'Epoch\[\d+\] Batch.*', logfile)

    for value in epoch_values:
        epoch, speed = parse_epoch_line(value)
        all_epoch_vals.append(speed)
        if epoch == 0:
            epoch_zero_vals.append(speed)
    return epoch_zero_vals, all_epoch_vals


def parse_epoch_times(logfile):
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


def parse_file(logfile):
    epoch_zero_vals, all_epoch_vals = parse_epoch_values(logfile)
    epoch_zero_time, elapsed_time = parse_epoch_times(logfile)
    results = Results(average(epoch_zero_vals),
                      epoch_zero_time,
                      elapsed_time,
                      average(all_epoch_vals))
    return results


def find_num_nodes(logfile):
    clear_cache_command = re.findall(r'srun.*Clearing cache on ', logfile)
    n_tasks = re.findall(r'ntasks=\d+', clear_cache_command[0])
    num_nodes = n_tasks[0].replace('ntasks=', '')
    return num_nodes


def read_files(logfiles):
    all_results = []
    prev_nodes_found = None

    for filename in logfiles:
        with open(filename, 'r') as logpointer:
            log = logpointer.read()
            results = parse_file(log)
            all_results.append(results)
            nodes_tested = find_num_nodes(log)
            if prev_nodes_found and nodes_tested != prev_nodes_found:
                raise ValueError('Error: Mixed node sizes found in log files!')
            prev_nodes_found = nodes_tested
    aggregate = Aggregate(
        [result.epoch_zero_speed for result in all_results],
        [result.epoch_zero_time for result in all_results],
        [result.elapsed_time for result in all_results],
        [result.average_speed for result in all_results]
    )
    return aggregate, nodes_tested


def print_averages(results, directory, nodes_tested):
    e_zero_speed = average(results.epoch_zero_speeds)
    e_zero_time = ms_to_seconds(average(results.epoch_zero_times))
    overall_speed = average(results.average_speeds)
    overall_time = ms_to_minutes(average(results.elapsed_times))

    output = f"""MLPerf Results:
Directory name: {directory}
Number of iterations: {len(results.epoch_zero_speeds)}
Nodes tested: {nodes_tested}
Epoch 0:
    Speed: {e_zero_speed} images/second
    Average time: {e_zero_time} seconds
Overall:
    Speed: {overall_speed} images/second
    Average time: {overall_time} minutes"""
    print(output)


def main():
    args = parse_args()
    logfiles = get_files(args.directory)
    aggregate, nodes_tested = read_files(logfiles)
    print_averages(aggregate, args.directory, nodes_tested)


if __name__ == '__main__':
    main()
