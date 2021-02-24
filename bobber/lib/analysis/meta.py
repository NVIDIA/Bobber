# SPDX-License-Identifier: MIT
import re


def avg(stats):
    if len(stats) > 0:
        return sum(stats) / len(stats)
    else:
        return 0.0


def pull_stats(summary):
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


def parse_summary(log_contents):
    summary = re.findall('---------.*-- finished', log_contents, re.DOTALL)
    if len(summary) == 0:
        return None
    # `summary` is a single-element list where the element is a list of all of
    # the metadata stats. The first and last lines are unecessary as they are
    # only used to parse the table and can be dropped.
    summary = summary[0].split('\n')[1:-1]
    return summary


def aggregate_results(combined_results):
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


def parse_meta_file(log_files, systems, results):
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
