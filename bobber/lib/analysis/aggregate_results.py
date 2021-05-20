# SPDX-License-Identifier: MIT
from functools import wraps
from typing import NoReturn


def average_decorator(func: 'method') -> float:
    """
    A simple wrapper to calculate the average of a list.

    This wrapper can be used on any function or method which returns a list of
    ints or floats and calculates the average of those values. If the average
    can't be calculated for any reason, the value will default to 0.0.

    Parameters
    ----------
    func : function/method
        A function to be wrapped with the average decorator.

    Returns
    -------
    float
        Returns a ``float`` of the final average value from the list.
    """
    @wraps(func)
    def wrapper(*args):
        value = func(*args)
        try:
            return sum(value) / len(value)
        except (TypeError, ValueError, ZeroDivisionError):
            return 0.0
    return wrapper


class AggregateResults:
    """
    Determine the aggregate values for all results.

    Bobber test runs typically include multiple iterations of all tests in an
    attempt to eliminiate noise. In order to find the true result, all
    iterations from a single test pass are averaged together. This is done on a
    per-system count level where all N-iterations of the single-node tests are
    aggregated together, then all N-iterations of the two-node tests (if
    applicable) are aggregated together, and so on.

    This class has a few helper methods to make it easy to output all data to
    both JSON format and a string representing the results.

    Parameters
    ----------
    read_bw : dict
        A ``dictionary`` containing all of the fio read bandwidth results for
        N-systems.
    write_bw : dict
        A ``dicitonary`` containing all of the fio write bandwidth results for
        N-systems.
    read_bw_params : dict
        A ``dictionary`` of the parameters used during the fio read bandwdith
        tests.
    write_bw_params : dict
        A ``dictionary`` of the parameters used during the fio write bandwidth
        tests.
    read_iops : dict
        A ``dictionary`` containing all of the fio read iops results for
        N-systems.
    write_iops : dict
        A ``dictionary`` containing all of the fio write iops results for
        N-systems.
    read_iops_params : dict
        A ``dictionary`` of the parameters used during the fio read iops tests.
    write_iops_params : dict
        A ``dictionary`` of the parameters used during the fio write iops
        tests.
    read_125k_bw : dict
        A ``dictionary`` containing all of the fio 125k read bandwidth results
        for N-systems.
    write_125k_bw : dict
        A ``dictionary`` containing all of the fio 125k write bandwidth results
        for N-systems.
    read_125k_bw_params : dict
        A ``dictionary`` of the parameters used during the fio 125k read
        bandwidth tests.
    write_125k_bw_params : dict
        A ``dictionary`` of the parameters used during the fio 125k write
        bandwidth tests.
    max_bw : dict
        A ``dictionary`` of the maximum bus bandwidth achieved from NCCL tests.
    bytes_sizes : dict
        A ``dictionary`` of the byte size used when the maximum bus bandwidth
        was achieved for NCCL tests.
    dali_results : dict
        A ``dictionary`` of the DALI throughput for all image sizes and types
        in images/second.
    metadata : dict
        A ``dictionary`` of the max, min, and mean values for all metadata
        operations.
    systems : int
        An ``int`` for the number of systems the current results represent.
    """
    def __init__(self,
                 read_bw: dict,
                 write_bw: dict,
                 read_bw_params: dict,
                 write_bw_params: dict,
                 read_iops: dict,
                 write_iops: dict,
                 read_iops_params: dict,
                 write_iops_params: dict,
                 read_125k_bw: dict,
                 write_125k_bw: dict,
                 read_125k_bw_params: dict,
                 write_125k_bw_params: dict,
                 max_bw: dict,
                 bytes_sizes: dict,
                 dali_results: dict,
                 metadata: dict,
                 systems: int) -> NoReturn:
        self._read_bw = read_bw
        self._read_bw_params = read_bw_params
        self._read_iops = read_iops
        self._read_iops_params = read_iops_params
        self._125k_read_bw = read_125k_bw
        self._125k_read_bw_params = read_125k_bw_params
        self._write_bw = write_bw
        self._write_bw_params = write_bw_params
        self._write_iops = write_iops
        self._write_iops_params = write_iops_params
        self._125k_write_bw = write_125k_bw
        self._125k_write_bw_params = write_125k_bw_params
        self._max_bw = max_bw
        self._bytes_sizes = bytes_sizes
        self._dali_results = dali_results
        self._metadata = metadata
        self._num_systems = systems

    def __str__(self) -> str:
        """
        A helper function to display results in human-readable text.

        Find the aggregate results for each test for N-systems and return the
        final output as a string, similar to the following:

        Systems tested: 1
        Aggregate Read Bandwidth: 1.595  GB/s
        Aggregate Write Bandwidth: 1.232  GB/s
        Aggregate Read IOPS: 136.5 k IOPS
        Aggregate Write IOPS: 135.0 k IOPS
        Aggregate 125k Read Bandwidth: 1.595  GB/s
        Aggregate 125k Write Bandwidth: 1.232  GB/s
        NCCL Max Bus Bandwidth: 79.865 at 512.0 MB
        Mdtest
            Directory creation: 71406.29550000001 ops
            Directory stat: 2698234.1525 ops
            Directory removal: 16016.5275 ops
            File creation: 137218.586 ops
            File stat: 2705405.084 ops
            File read: 2230275.9365 ops
            File removal: 175736.5435 ops
            Tree creation: 1546.792 ops
            Tree removal: 5878.747 ops

        DALI Standard 800x600
            Min Speed: 2509.35 images/second (0.727 GB/s)
            Avg Speed: 2694.595 images/second (0.78 GB/s)
        DALI Standard 3840x2160
            Min Speed: 344.078 images/second (1.712 GB/s)
            Avg Speed: 430.854 images/second (2.144 GB/s)
        DALI TFRecord 800x600
            Min Speed: 2508.069 images/second (0.726 GB/s)
            Avg Speed: 2665.653 images/second (0.772 GB/s)
        DALI TFRecord 3840x2160
            Min Speed: 317.276 images/second (1.579 GB/s)
            Avg Speed: 376.862 images/second (1.875 GB/s)

        Returns
        -------
        str
            Returns a ``string`` of the final aggregate results for N-systems.
        """
        values_to_print = [
            # [Field name, value, unit]
            ['Systems tested:', self._num_systems, ''],
            ['Aggregate Read Bandwidth:', self.average_read_bw, ' GB/s'],
            ['Aggregate Write Bandwidth:', self.average_write_bw, ' GB/s'],
            ['Aggregate 125k Read Bandwidth:', self.average_125k_read_bw,
             ' GB/s'],
            ['Aggregate 125k Write Bandwidth:', self.average_125k_write_bw,
             ' GB/s'],
            ['Aggregate Read IOPS:', self.average_read_iops, 'k IOPS'],
            ['Aggregate Write IOPS:', self.average_write_iops, 'k IOPS'],
        ]
        output = ''
        for item in values_to_print:
            field, value, unit = item
            if value:
                output += f'{field} {value} {unit}\n'
        if round(self.max_bus_bandwidth, 3) != 0.0:
            output += ('NCCL Max Bus Bandwidth: '
                       f'{round(self.max_bus_bandwidth, 3)} '
                       f'at {self.max_bus_bytes / 1024 / 1024} MB')

        if self._metadata:
            output += '\n'
            output += self._metadata_print()

        if self._dali_results_print('800x600 standard jpg'):
            output += (f"""
DALI Standard 800x600{self._dali_results_print('800x600 standard jpg')}
DALI Standard 3840x2160{self._dali_results_print('3840x2160 standard jpg')}
DALI TFRecord 800x600{self._dali_results_print('800x600 tfrecord')}
DALI TFRecord 3840x2160{self._dali_results_print('3840x2160 tfrecord')}
""")
        else:
            output += '\n'
        return output

    def _metadata_print(self) -> str:
        """
        Determine and return the metadata results.

        Iterate through all of the final metadata results for each operation
        type and generate the aggregate number of operations for all
        iterations.

        Returns
        -------
        str
            Returns a ``string`` of the formated metadata results.
        """
        output = 'Mdtest\n'

        if self._metadata[self._num_systems] == '':
            return ''
        for key, values in self._metadata[self._num_systems].items():
            output += (f"    {key}: {values['mean']} ops\n")
        return output

    def _dali_results_print(self, size: str) -> str:
        """
        Determine and return the DALI results.

        Calculate the minimum and average speed in images/second and the
        resulting bandwidth for each image type and format and return the
        result as a string.

        Parameters
        ----------
        size : str
            The size and type of image to parse, such as '800x600 tfrecord'.

        Returns
        -------
        str
            Returns a ``string`` of the formated DALI results.
        """
        try:
            dali_results = self._dali_results[self._num_systems]
        except KeyError:
            return ''
        min_speed = round(dali_results[size]['min images/second'], 3)
        min_bw = round(dali_results[size]['min bandwidth'] * 1e-9, 3)
        avg_speed = round(dali_results[size]['average images/second'], 3)
        avg_bw = round(dali_results[size]['average bandwidth'] * 1e-9, 3)

        output = (f"""
    Min Speed: {min_speed} images/second ({min_bw} GB/s)
    Avg Speed: {avg_speed} images/second ({avg_bw} GB/s)""")
        return output

    @property
    def json(self) -> dict:
        """
        Generate a JSON representation of the results.

        Creating a JSON dump of the results makes it easier for remote tools to
        archive or display results in an easily ingestible format, such as
        webpages or databases.

        Returns
        -------
        dict
            Returns a JSON-parsable ``dictionary`` representation of all of the
            results including parameters and units where applicable.
        """
        results = {
            'systems_tested': self._num_systems,
            'bandwidth': {
                'read': self._average_read_bw(),
                'write': self._average_write_bw(),
                'unit': 'bytes/second',
                'parameters': {
                    'read': self._read_bw_params,
                    'write': self._write_bw_params
                }
            },
            'iops': {
                'read': self._average_read_iops(),
                'write': self._average_write_iops(),
                'unit': 'operations/second',
                'parameters': {
                    'read': self._read_iops_params,
                    'write': self._write_iops_params
                }
            },
            '125k_bandwidth': {
                'read': self._average_125k_read_bw(),
                'write': self._average_125k_write_bw(),
                'unit': 'operations/second',
                'parameters': {
                    'read': self._125k_read_bw_params,
                    'write': self._125k_write_bw_params
                }
            },
            'nccl': {
                'max_bus_bw': self.max_bus_bandwidth,
                'max_bus_bytes': self.max_bus_bytes,
                'max_bus_bw_units': 'GB/s'
            }
        }
        try:
            results['dali'] = self._dali_results[self._num_systems]
        except KeyError:
            results['dali'] = {}
        return results

    @average_decorator
    def _average_read_bw(self) -> float:
        """
        Returns the average read bandwidth as a ``float`` for all iterations
        in B/s. Defaults to 0.0.
        """
        try:
            return self._read_bw[self._num_systems]
        except KeyError:
            return 0.0

    @property
    def average_read_bw(self) -> float:
        """
        Returns the average read bandwidth as a ``float`` for all iterations
        in GB/s, rounded to the nearest thousandth.
        """
        return round(self._average_read_bw() * 1e-9, 3)

    @average_decorator
    def _average_write_bw(self) -> float:
        """
        Returns the average write bandwidth as a ``float`` for all iterations
        in B/s. Defaults to 0.0
        """
        try:
            return self._write_bw[self._num_systems]
        except KeyError:
            return 0.0

    @property
    def average_write_bw(self) -> float:
        """
        Returns the average write bandwidth as a ``float`` for all iterations
        in GB/s, rounded to the nearest thousandth.
        """
        return round(self._average_write_bw() * 1e-9, 3)

    @average_decorator
    def _average_125k_read_bw(self) -> float:
        """
        Returns the average 125k read bandwidth as a ``float`` for all
        iterations in B/s. Defaults to 0.0.
        """
        try:
            return self._125k_read_bw[self._num_systems]
        except KeyError:
            return 0.0

    @property
    def average_125k_read_bw(self) -> float:
        """
        Returns the average 125k read bandwidth as a ``float`` for all
        iterations in GB/s, rounded to the nearest thousandth.
        """
        return round(self._average_125k_read_bw() * 1e-9, 3)

    @average_decorator
    def _average_125k_write_bw(self) -> float:
        """
        Returns the average 125k write bandwidth as a ``float`` for all
        iterations in B/s. Defaults to 0.0
        """
        try:
            return self._125k_write_bw[self._num_systems]
        except KeyError:
            return 0.0

    @property
    def average_125k_write_bw(self) -> float:
        """
        Returns the average 125k write bandwidth as a ``float`` for all
        iterations in GB/s, rounded to the nearest thousandth.
        """
        return round(self._average_125k_write_bw() * 1e-9, 3)

    @average_decorator
    def _average_read_iops(self) -> float:
        """
        Returns the average read IOPS as a ``float`` for all iterations in
        ops/second. Defaults to 0.0.
        """
        try:
            return self._read_iops[self._num_systems]
        except KeyError:
            return 0.0

    @property
    def average_read_iops(self) -> float:
        """
        Returns the average read IOPS as a ``float`` for all iterations in K
        ops/second.
        """
        return round(self._average_read_iops() * 1e-3, 3)

    @average_decorator
    def _average_write_iops(self) -> float:
        """
        Returns the average write IOPS as a ``float`` for all iterations in
        ops/second. Defaults to 0.0.
        """
        try:
            return self._write_iops[self._num_systems]
        except KeyError:
            return 0.0

    @property
    def average_write_iops(self) -> float:
        """
        Returns the average write IOPS as a ``float`` for all iterations in K
        ops/second.
        """
        return round(self._average_write_iops() * 1e-3, 3)

    @property
    @average_decorator
    def max_bus_bandwidth(self) -> float:
        """
        Returns the average of the maximum bandwidth achieved as a ``float``
        in NCCL in GB/s. Defaults to 0.0
        """
        try:
            return self._max_bw[self._num_systems]
        except KeyError:
            return 0.0

    @property
    def max_bus_bytes(self) -> float:
        """
        Returns the associated byte size for the maximum bandwidth achieved in
        NCCL as a ``float``. Defaults to 0.0
        """
        try:
            return int(max(self._bytes_sizes[self._num_systems],
                           key=self._bytes_sizes[self._num_systems].count))
        except (ValueError, KeyError):
            return 0.0
