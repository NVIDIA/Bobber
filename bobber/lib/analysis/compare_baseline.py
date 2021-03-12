# SPDX-License-Identifier: MIT
import sys
from bobber.lib.constants import BASELINES
from bobber.lib.exit_codes import BASELINE_FAILURE
from bobber.lib.analysis.common import bcolors
from bobber.lib.system.file_handler import read_yaml
from typing import NoReturn, Optional, Tuple


# Map the dicitonary keys in the baseline to human-readable names.
TEST_MAPPING = {
    'bandwidth': 'FIO Bandwidth',
    'iops': 'FIO IOPS',
    'nccl': 'NCCL',
    'dali': 'DALI'
}


def metric_passes(expected: float, got: float, tolerance: int) -> bool:
    """
    Determine if a test result meets a particular threshold.

    Compares the parsed value with the requested baseline for the same test and
    return a boolean of whether or not it is greater than expected. If a
    tolerance is passed, any value that is N-percent or higher below the
    requested tolerance of N will still be marked as passing.

    Parameters
    ----------
    expected : float
        A ``float`` of the baseline value to compare against.
    got : float
        A ``float`` of the test result that was parsed.
    tolerance : int
        An ``int`` of the percentage below the threshold to still mark as
        passing.

    Returns
    -------
    bool
        Returns a ``boolean`` which evaluates to `True` when the parsed value
        is greater than the baseline and `False` otherwise.
    """
    if tolerance > 0:
        # If user passes a 5% tolerance, multiply the expected value by 5% less
        # than current value to get the tolerance.
        expected = (1 - tolerance / 100) * expected
    if got > expected:
        return True
    else:
        return False


def result_text(result: bool, failures: int) -> Tuple[str, int]:
    """
    Color-code the result output.

    If the result passes the threshold, it will be marked as PASSing in green
    text. Otherwise, it will be marked as FAILing in red text.

    Parameters
    ----------
    result : bool
        A ``boolean`` which evaluates to `True` when the value meets the
        threshold and `False` if not.
    failures : int
        An ``integer`` of the number of results that have not met the
        threshold.

    Returns
    -------
    tuple
        Returns a ``tuple`` of (``str``, ``int``) representing the color-coded
        text and the number of failures found, respectively.
    """
    if result:
        output = f'{bcolors.PASS}PASS{bcolors.ENDC}'
    else:
        failures += 1
        output = f'{bcolors.FAIL}FAIL{bcolors.ENDC}'
    return output, failures


def evaluate_fio(baselines: dict, results: dict, test_name: str, failures: int,
                 tolerance: int) -> int:
    """
    Evaluate the fio test results against the baseline.

    Determine if the fio test results meet the expected threshold and display
    the outcome with appropriate units.

    Parameters
    ----------
    baselines : dict
        A ``dictionary`` of the baseline to compare results against.
    results : dict
        A ``dictionary`` of the parsed results.
    test_name : str
        A ``string`` of the name of the test being parsed.
    failures : int
        An ``integer`` of the number of results that have not met the
        threshold.
    tolerance : int
        An ``int`` of the percentage below the threshold to still mark as
        passing.

    Returns
    -------
    int
        Returns an ``integer`` of the number of results that have not met the
        threshold.
    """
    for test, value in baselines.items():
        if test_name not in results.keys():
            continue
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
        result = metric_passes(expected, got, tolerance)
        output, failures = result_text(result, failures)
        text += f', Result: {output}'
        print(text)
    return failures


def evaluate_nccl(baseline: dict, results: dict, failures: int,
                  tolerance: int) -> int:
    """
    Evaluate the NCCL test results against the baseline.

    Determine if the NCCL test results meet the expected threshold and display
    the outcome with appropriate units.

    Parameters
    ----------
    baselines : dict
        A ``dictionary`` of the baseline to compare results against.
    results : dict
        A ``dictionary`` of the parsed results.
    failures : int
        An ``integer`` of the number of results that have not met the
        threshold.
    tolerance : int
        An ``int`` of the percentage below the threshold to still mark as
        passing.

    Returns
    -------
    int
        Returns an ``integer`` of the number of results that have not met the
        threshold.
    """
    if 'max_bus_bw' not in baseline.keys():
        return failures
    print('  NCCL Max Bus Bandwidth (GB/s)')
    expected = baseline['max_bus_bw']
    got = results['nccl']['max_bus_bw']
    text = f'    Expected: {expected}, Got: {got}'
    result = metric_passes(expected, got, tolerance)
    output, failures = result_text(result, failures)
    text += f', Result: {output}'
    print(text)
    return failures


def evaluate_dali(baselines: dict, results: dict, test_name: str,
                  failures: int, tolerance: int) -> int:
    """
    Evaluate the DALI test results against the baseline.

    Determine if the DALI test results meet the expected threshold and display
    the outcome with appropriate units.

    Parameters
    ----------
    baselines : dict
        A ``dictionary`` of the baseline to compare results against.
    results : dict
        A ``dictionary`` of the parsed results.
    test_name : str
        A ``string`` of the name of the test being parsed.
    failures : int
        An ``integer`` of the number of results that have not met the
        threshold.
    tolerance : int
        An ``int`` of the percentage below the threshold to still mark as
        passing.

    Returns
    -------
    int
        Returns an ``integer`` of the number of results that have not met the
        threshold.
    """
    for test, value in baselines.items():
        if test not in results.keys():
            continue
        print(f'  DALI {test} (images/second)')
        expected = value
        got = round(results[test]['average images/second'], 3)
        text = f'    Expected: {expected}, Got: {got}'
        result = metric_passes(expected, got, tolerance)
        output, failures = result_text(result, failures)
        text += f', Result: {output}'
        print(text)
    return failures


def evaluate_test(baseline: dict, results: dict, system_count: int,
                  tolerance: int, failures: int) -> int:
    """
    Evaluate all tests for N-nodes and compare against the baseline.

    The comparison verifies results meet a certain threshold for each system
    count in a sweep. For example, in an 8-node sweep, compare the one-node
    results to the baseline before comparing the two-node results and so on.

    Parameters
    ----------
    baseline : dict
        A ``dictionary`` of the baseline to compare results against.
    results : dict
        A ``dictionary`` of the parsed results.
    system_count : int
        An ``int`` of the number of systems that were tested for each
        comparison level.
    tolerance : int
        An ``int`` of the percentage below the threshold to still mark as
        passing.
    failures : int
        An ``integer`` of the number of results that have not met the
        threshold.

    Returns
    -------
    int
        Returns an ``integer`` of the number of results that have not met the
        threshold.
    """
    for test_name, test_values in baseline.items():
        print('-' * 80)
        if test_name in ['bandwidth', 'iops']:
            failures = evaluate_fio(test_values, results, test_name, failures,
                                    tolerance)
        elif test_name == 'nccl':
            failures = evaluate_nccl(test_values, results, failures, tolerance)
        elif test_name == 'dali':
            failures = evaluate_dali(test_values,
                                     results['dali'],
                                     test_name,
                                     failures,
                                     tolerance)
    return failures


def compare_baseline(results: dict, baseline: str, tolerance: int,
                     custom: Optional[bool] = False) -> NoReturn:
    """
    Compare a baseline against parsed results.

    Pull the requested baseline either from a custom YAML file or one of the
    existing baselines included with the application and compare against the
    parsed results by checking if the parsed result is greater than the
    baseline on a per-system basis.

    Parameters
    ----------
    results : dict
        A ``dictionary`` of the complete set of results from a parsed
        dictionary.
    baseline : str
        A ``string`` of the baseline to use. This either represents a key from
        the included baselines, or a filename to a custom YAML config file to
        read.
    tolerance : int
        An ``int`` of the tolerance as a percentage below the baseline to allow
        results to still be marked as passing.
    custom : bool (optional)
        An optional ``boolean`` that, when `True`, will read in a baseline
        passed from a YAML file. If `False`, it will compare against an
        included baseline.
    """
    failures = 0

    print('=' * 80)
    print('Baseline assessment')
    if custom:
        print('Comparing against a custom config')
        baseline = read_yaml(baseline)
    else:
        print(f'Comparing against "{baseline}"')
        baseline = BASELINES[baseline]
    if tolerance > 0:
        print(f'Allowing a tolerance of {tolerance}% below expected to PASS')

    for system_count, baseline_results in baseline['systems'].items():
        print('=' * 80)
        if str(system_count) not in results['systems'].keys():
            print(f'No results found for {system_count} system(s)')
            print('Skipping...')
            continue
        print(f' {system_count} System(s)')
        failures = evaluate_test(baseline_results,
                                 results['systems'][str(system_count)],
                                 system_count,
                                 tolerance,
                                 failures)

    if failures > 0:
        print('-' * 80)
        print(f'{failures} test(s) did not meet the suggested criteria!')
        print('See results above for failed tests and verify setup.')
        # Throw a non-zero exit status so any tools that read codes will catch
        # that the baseline was not met.
        sys.exit(BASELINE_FAILURE)

    print('=' * 80)
