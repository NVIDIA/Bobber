# SPDX-License-Identifier: MIT
import re


def _clean_sizes(sizes):
    return [int(size.replace('in bytes: ', '')) for size in sizes]


def _size_parsing(log_contents):
    results_sub_dict = {
        'image size': 0,
        'size unit': 'B',
        'directory size': 0,
        'min images/second': 0,
        'average images/second': 0,
        'min bandwidth': 0,
        'average bandwidth': 0,
        'bandwidth unit': 'bytes/second'
    }
    results = {
        '800x600 standard jpg': results_sub_dict.copy(),
        '3840x2160 standard jpg': results_sub_dict.copy(),
        '800x600 tfrecord': results_sub_dict.copy(),
        '3840x2160 tfrecord': results_sub_dict.copy()
    }

    image_size = re.findall('First image size from .*\n.*', log_contents)
    if len(image_size) != 4:
        raise ValueError('Error: Incomplete DALI file. Missing information on'
                         ' file sizes')
    for line in image_size:
        sizes = re.findall(r'in bytes: \d+', line)
        if len(sizes) != 2:
            raise ValueError('Error: Missing data sizes in DALI log file.')
        image_size, directory_size = _clean_sizes(sizes)
        if '3840x2160' in line:
            results['3840x2160 standard jpg']['image size'] = image_size
            results['3840x2160 standard jpg']['directory size'] = \
                directory_size
            results['3840x2160 tfrecord']['image size'] = image_size
            results['3840x2160 tfrecord']['directory size'] = directory_size
        elif '800x600' in line:
            results['800x600 standard jpg']['image size'] = image_size
            results['800x600 standard jpg']['directory size'] = directory_size
            results['800x600 tfrecord']['image size'] = image_size
            results['800x600 tfrecord']['directory size'] = directory_size
    return results


def _average(input_list):
    try:
        return float(sum(input_list) / len(input_list))
    except ZeroDivisionError:
        return 0.0


def _update_results(image_type_match, results):
    size = image_type_match['image size']
    image_type_match['min images/second'] = min(results)
    image_type_match['average images/second'] = _average(results)
    image_type_match['min bandwidth'] = size * min(results)
    image_type_match['average bandwidth'] = size * _average(results)
    return image_type_match


def _result_parsing(log_contents, systems, image_results, log_file):
    # The result sections are in a strict order, allowing us to
    # deterministically match results with the corresponding image size and
    # type:
    # 0: 800x600 Standard File Read
    # 1: 3840x2160 Standard File Read
    # 2: 800x600 TFRecord
    # 3: 3840x2160 TFRecord
    image_type_match = [
        image_results['800x600 standard jpg'],
        image_results['3840x2160 standard jpg'],
        image_results['800x600 tfrecord'],
        image_results['3840x2160 tfrecord']
    ]

    test_sections = re.findall(r'RUN 1/1.*?OK', log_contents, re.DOTALL)
    if len(test_sections) != 4:
        print(f'Warning: Invalid number of results found in {log_file} log '
              'file. Skipping...')
        return {}

    for num, section in enumerate(test_sections):
        result_lines = re.findall('.*img/s', section)
        all_speeds = []

        for line in result_lines:
            speed = re.sub('.*speed: ', '', line)
            speed = float(speed.replace(' [img/s', ''))
            all_speeds.append(speed)

        # Per standard practices, the first N results for N systems is treated
        # as a warmup and discarded. Occasionally, the timing of results will
        # be off, and one node will showcase the 2nd test pass before all nodes
        # have finished the first. To accomodate for this, the lowest N results
        # are assumed to be the first test pass and are dropped.
        all_speeds = sorted(all_speeds)[systems:]
        image_type_match[num] = _update_results(image_type_match[num],
                                                all_speeds)

    # Rebuild the dictionary based on the updated results.
    image_results = {
        '800x600 standard jpg': image_type_match[0],
        '3840x2160 standard jpg': image_type_match[1],
        '800x600 tfrecord': image_type_match[2],
        '3840x2160 tfrecord': image_type_match[3]
    }
    return image_results


def _combine_results(results, systems):
    system_results = {}

    for image_type in ['800x600 standard jpg',
                       '3840x2160 standard jpg',
                       '800x600 tfrecord',
                       '3840x2160 tfrecord']:
        avg_min_speed, avg_avg_speed = [], []
        avg_min_bw, avg_avg_bw = [], []
        avg_img_size, avg_dir_size = [], []

        for result in results:
            if image_type not in result:
                continue
            avg_min_speed.append(result[image_type]['min images/second'])
            avg_avg_speed.append(result[image_type]['average images/second'])
            avg_min_bw.append(result[image_type]['min bandwidth'])
            avg_avg_bw.append(result[image_type]['average bandwidth'])
            avg_img_size.append(result[image_type]['image size'])
            avg_dir_size.append(result[image_type]['directory size'])

        # Multiply the average in all performance categories by the number of
        # systems tested to get an average aggregate throughput result for the
        # cluster.
        system_results[image_type] = {
            'image size': _average(avg_img_size),
            'size unit': 'B',
            'directory size': _average(avg_dir_size),
            'min images/second': _average(avg_min_speed) * systems,
            'average images/second': _average(avg_avg_speed) * systems,
            'min bandwidth': _average(avg_min_bw) * systems,
            'average bandwidth': _average(avg_avg_bw) * systems,
            'bandwidth unit': 'bytes/second'
        }
    return system_results


def parse_dali_file(log_files, systems, results_dict):
    results = []

    for log in log_files:
        with open(log, 'r') as f:
            log_contents = f.read()
        image_results = _size_parsing(log_contents)
        results.append(_result_parsing(log_contents,
                                       systems,
                                       image_results,
                                       log))
    results_dict[systems] = _combine_results(results, systems)
    return results_dict
