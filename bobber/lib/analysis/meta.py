# SPDX-License-Identifier: MIT
import re


def avg(stats: list) -> float:
    """
    Find the average of a list.

    Given a list of numbers, calculate the average of all values in the list.
    If the list is empty, default to 0.0.

    Parameters
    ----------
    input_list : list
        A ``list`` of ``floats`` to find an average of.

    Returns
    -------
    float
        Returns a ``float`` of the average value of the list.
    """
    if len(stats) > 0:
        return sum(stats) / len(stats)
    else:
        return 0.0


def pull_stats(summary: list) -> dict:
    """
    Convert stats to a dictionary.

    Each line in the summary table in the log file needs to be parsed by first
    converting the table to a comma-separated list for easy parsing, then
    taking the first column as the statistical category and placing the
    remaining values into maximum, minimum, mean, and standard deviation.

    Parameters
    ----------
    summary : list
        A ``list`` of ``strings`` representing each line in the summary table
        of the metadata file.

    Returns
    -------
    dict
        Returns a ``dictionary`` of the converted table.
    """
    results = {}

    for stat in summary:
        # Convert the table to a comma-separated list to make it easier to
        # parse.
        stat = stat.replace(':', '')
        stat_csv = re.sub('  +', ',', stat.strip())
        components = stat_csv.split(',')
        key, max_val, min_val, mean, stdev = components
        results[key] = {
            'max': float(max_val),
            'min': float(min_val),
            'mean': float(mean),
            'stdev': float(stdev)
        }
    return results


def parse_summary(log_contents: str) -> list:
    """
    Pull the summary table from the metadata log.

    The bottom of the metadata log contains a summary table with all of the
    individual metadata operations and the results from the test. This table is
    denoted by a line of '-' signs and is ended with '-- finished'. Since these
    lines are used to make parsing easier, they should be dropped in the end.

    Parameters
    ----------
    log_contents : str
        A ``string`` of the contents of the entire contents of a metadata log
        file.

    Returns
    -------
    list
        Returns a ``list`` of ``strings`` representing each line in the summary
        table.
    """
    summary = re.findall('---------                      .*-- finished',
                         log_contents, re.DOTALL)
    if len(summary) == 0:
        return None
    # `summary` is a single-element list where the element is a list of all of
    # the metadata stats. The first and last lines are unecessary as they are
    # only used to parse the table and can be dropped.
    summary = summary[0].split('\n')[1:-1]
    return summary


def aggregate_results(combined_results: list) -> dict:
    """
    Find the aggregate results for all categories.

    Parse every result from the metadata log files and capture the min, max,
    and mean for each operation for all iterations in a single object.

    Parameters
    ----------
    combined_results : list
        A ``list`` of ``dictionaries`` containing the results from each summary
        table in each log file.

    Returns
    -------
    dict
        Returns a ``dictionary`` of the final aggregate results for each
        operation in the summary tables of all logs.
    """
    final_aggregate = {}

    if len(combined_results) == 0:
        return final_aggregate

    for key, stats in combined_results[0].items():
        key_metrics = [stat[key] for stat in combined_results]
        final_aggregate[key] = {
            'max': max([result['max'] for result in key_metrics]),
            'min': min([result['min'] for result in key_metrics]),
            'mean': avg([result['mean'] for result in key_metrics])
        }
    return final_aggregate


def parse_meta_file(log_files: list, systems: int, results: dict) -> dict:
    """
    Parse the metadata results from the metadata logs.

    Search through each metadata log and extract the operations in the summary
    table, saving the aggregate results in a dictionary.

    Parameters
    ----------
    log_files : list
        A ``list`` of ``strings`` of the filename of each metadata log file in
        the results directory.
    systems : int
        An ``integer`` of the number of systems used during the current test.
    results : dict
        A ``dictionary`` of the aggregate metadata results for each system
        count.

    Returns
    -------
    dict
        Returns an updated ``dictionary`` including the aggregate metadata
        results for N-systems.
    """
    combined_results = []

    for log in log_files:
        with open(log, 'r') as f:
            log_contents = f.read()
        summary = parse_summary(log_contents)
        if not summary:
            print(f'Warning: Invalid results found in {log} log file.')
            print('Skipping...')
            continue
        stats = pull_stats(summary)
        combined_results.append(stats)
    results[systems] = aggregate_results(combined_results)
    return results
