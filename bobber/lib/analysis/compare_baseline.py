# SPDX-License-Identifier: MIT
import sys
from bobber.lib.constants import BASELINES
from bobber.lib.analysis.common import bcolors
from bobber.lib.system.file_handler import read_yaml


# Map the dicitonary keys in the baseline to human-readable names.
TEST_MAPPING = {
    'bandwidth': 'FIO Bandwidth',
    'iops': 'FIO IOPS',
    'nccl': 'NCCL',
    'dali': 'DALI'
}


def metric_passes(expected, got):
    if got > expected:
        return True
    else:
        return False


def result_text(result, failures):
    if result:
        output = f'{bcolors.PASS}PASS{bcolors.ENDC}'
    else:
        failures += 1
        output = f'{bcolors.FAIL}FAIL{bcolors.ENDC}'
    return output, failures


def evaluate_fio(baselines, results, test_name, failures):
    for test, value in baselines.items():
        if test_name == 'bandwidth':
            unit = '(GB/s)'
            expected = value / 1000000000
            got = round(results[test_name][test] / 1000000000, 3)
        elif test_name == 'iops':
            unit = '(k IOPS)'
            expected = value / 1000
            got = round(results[test_name][test] / 1000, 3)
        print(f'  {TEST_MAPPING[test_name]} {test.title()} {unit}')
        text = f'    Expected: {expected}, Got: {got}'
        result = metric_passes(expected, got)
        output, failures = result_text(result, failures)
        text += f', Result: {output}'
        print(text)
    return failures


def evaluate_nccl(baseline, results, failures):
    print('  NCCL Max Bus Bandwidth (GB/s)')
    expected = baseline['max_bus_bw']
    got = results['nccl']['max_bus_bw']
    text = f'    Expected: {expected}, Got: {got}'
    result = metric_passes(expected, got)
    output, failures = result_text(result, failures)
    text += f', Result: {output}'
    print(text)
    return failures


def evaluate_dali(baselines, results, test_name, failures):
    for test, value in baselines.items():
        print(f'  DALI {test} (images/second)')
        expected = value
        got = round(results[test]['average images/second'], 3)
        text = f'    Expected: {expected}, Got: {got}'
        result = metric_passes(expected, got)
        output, failures = result_text(result, failures)
        text += f', Result: {output}'
        print(text)
    return failures


def evaluate_test(baseline, results, system_count):
    failures = 0

    for test_name, test_values in baseline.items():
        print('-' * 80)
        if test_name in ['bandwidth', 'iops']:
            failures = evaluate_fio(test_values, results, test_name, failures)
        elif test_name == 'nccl':
            failures = evaluate_nccl(test_values, results, failures)
        elif test_name == 'dali':
            failures = evaluate_dali(test_values,
                                     results['dali'],
                                     test_name,
                                     failures)

    if failures > 0:
        print('-' * 80)
        print(f'{failures} tests did not meet the suggested criteria!')
        print('See results above for failed tests and verify setup.')
        # Throw a non-zero exit status so any tools that read codes will catch
        # that the baseline was not met.
        sys.exit(1)


def compare_baseline(results, baseline, custom=False):
    print('=' * 80)
    print('Baseline assessment')
    if custom:
        print('Comparing against a custom config')
        baseline = read_yaml(baseline)
    else:
        print(f'Comparing against "{baseline}"')
        baseline = BASELINES[baseline]

    for system_count, baseline_results in baseline['systems'].items():
        print('=' * 80)
        print(f' {system_count} System(s)')
        evaluate_test(baseline_results,
                      results['systems'][str(system_count)],
                      system_count)

    print('=' * 80)
