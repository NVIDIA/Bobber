# SPDX-License-Identifier: MIT
from functools import wraps


def average_decorator(func):
    @wraps(func)
    def wrapper(*args):
        value = func(*args)
        try:
            return sum(value) / len(value)
        except (TypeError, ValueError, ZeroDivisionError):
            return 0.0
    return wrapper


class AggregateResults:
    def __init__(self,
                 read_bw,
                 write_bw,
                 read_bw_params,
                 write_bw_params,
                 read_iops,
                 write_iops,
                 read_iops_params,
                 write_iops_params,
                 max_bw,
                 bytes_sizes,
                 dali_results,
                 metadata,
                 systems):
        self._read_bw = read_bw
        self._read_bw_params = read_bw_params
        self._read_iops = read_iops
        self._read_iops_params = read_iops_params
        self._write_bw = write_bw
        self._write_bw_params = write_bw_params
        self._write_iops = write_iops
        self._write_iops_params = write_iops_params
        self._max_bw = max_bw
        self._bytes_sizes = bytes_sizes
        self._dali_results = dali_results
        self._metadata = metadata
        self._num_systems = systems

    def __str__(self):
        values_to_print = [
            # [Field name, value, unit]
            ['Systems tested:', self._num_systems, ''],
            ['Aggregate Read Bandwidth:', self.average_read_bw, ' GB/s'],
            ['Aggregate Write Bandwidth:', self.average_write_bw, ' GB/s'],
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

    def _metadata_print(self):
        output = 'Mdtest\n'

        if self._metadata[self._num_systems] == '':
            return ''
        for key, values in self._metadata[self._num_systems].items():
            output += (f"    {key}: {values['mean']} ops\n")
        return output

    def _dali_results_print(self, size):
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
    def json(self):
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
    def _average_read_bw(self):
        """
        Returns the average read bandwidth for all iterations in B/s.
        """
        try:
            return self._read_bw[self._num_systems]
        except KeyError:
            return 0.0

    @property
    def average_read_bw(self):
        """
        Returns the average read bandwidth for all iterations in GB/s, rounded
        to the nearest thousandth.
        """
        return round(self._average_read_bw() * 1e-9, 3)

    @average_decorator
    def _average_write_bw(self):
        """
        Returns the average write bandwidth for all iterations in B/s.
        """
        try:
            return self._write_bw[self._num_systems]
        except KeyError:
            return 0.0

    @property
    def average_write_bw(self):
        """
        Returns the average write bandwidth for all iterations in GB/s, rounded
        to the nearest thousandth.
        """
        return round(self._average_write_bw() * 1e-9, 3)

    @average_decorator
    def _average_read_iops(self):
        """
        Returns the average read IOPS for all iterations in ops/second.
        """
        try:
            return self._read_iops[self._num_systems]
        except KeyError:
            return 0.0

    @property
    def average_read_iops(self):
        """
        Returns the average read IOPS for all iterations in K ops/second.
        """
        return round(self._average_read_iops() * 1e-3, 3)

    @average_decorator
    def _average_write_iops(self):
        """
        Returns the average write IOPS for all iterations in ops/second.
        """
        try:
            return self._write_iops[self._num_systems]
        except KeyError:
            return 0.0

    @property
    def average_write_iops(self):
        """
        Returns the average write IOPS for all iterations in K ops/second.
        """
        return round(self._average_write_iops() * 1e-3, 3)

    @property
    @average_decorator
    def max_bus_bandwidth(self):
        """
        Returns the average of the maximum bandwidth achieved in NCCL in GB/s.
        """
        try:
            return self._max_bw[self._num_systems]
        except KeyError:
            return 0.0

    @property
    def max_bus_bytes(self):
        """
        Returns the associated byte size for the maximum bandwidth achieved in
        NCCL.
        """
        try:
            return int(max(self._bytes_sizes[self._num_systems],
                           key=self._bytes_sizes[self._num_systems].count))
        except (ValueError, KeyError):
            return 0.0
