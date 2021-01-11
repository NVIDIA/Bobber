# SPDX-License-Identifier: MIT
BUILD = 'build'
EXPORT = 'export'
CAST = 'cast'
LOAD = 'load'
PARSE_RESULTS = 'parse-results'
RUN_ALL = 'run-all'
RUN_DALI = 'run-dali'
RUN_NCCL = 'run-nccl'
RUN_STG_BW = 'run-stg-bw'
RUN_STG_IOPS = 'run-stg-iops'
RUN_STG_META = 'run-stg-meta'

DGX_A100_SINGLE = {
    'gpus': 8,
    'bw_threads': 16,
    'iops_threads': 200,
    'batch_size_sm': 512,
    'batch_size_lg': 256,
    'ssh_iface': 'enp226s0',
    'nccl_ib_hcas': 'mlx5_0,mlx5_1,mlx5_2,mlx5_3,mlx5_4,mlx5_5,mlx5_6,mlx5_7',
    'nccl_max': 4
}

DGX_A100_DUAL = {
    'gpus': 8,
    'bw_threads': 16,
    'iops_threads': 200,
    'batch_size_sm': 512,
    'batch_size_lg': 256,
    'ssh_iface': 'enp226s0',
    'nccl_ib_hcas': 'mlx5_0,mlx5_1,mlx5_2,mlx5_3,mlx5_6,mlx5_7,mlx5_8,mlx5_9',
    'nccl_max': 4
}

DGX_2 = {
    'gpus': 16,
    'bw-threads': 16,
    'batch-size-sm': 150,
    'batch-size-lg': 75,
    'iops-threads': 80,
    'ssh-iface': 'enp6s0',
    'nccl-ib-hcas':
    'mlx5_13,mlx5_15,mlx5_17,mlx5_19,mlx5_3,mlx5_5,mlx5_7,mlx5_9',
    'nccl-max': 1
}

SYSTEMS = {
    'dgx-a100-single': DGX_A100_SINGLE,
    'dgx-a100-dual': DGX_A100_DUAL,
    'dgx-2': DGX_2
}

# Baseline Results
# This is considered a minimum value that tests should hit in order to be
# verified the system has been configured properly for HPC and AI workloads.
SINGLE_DGX_STATION_BASELINE = {
    'systems': {
        '1': {
            'bandwidth': {
                # FIO BW speed in bytes/second
                'read': 1200000000,
                'write': 1000000000
            },
            'iops': {
                # FIO IOPS speed in ops/second
                'read': 100000,
                'write': 100000
            },
            'nccl': {
                # NCCL maximum bus bandwidth in GB/s
                'max_bus_bw': 70
            },
            'dali': {
                # DALI average speed in images/second
                '800x600 standard jpg': 2000,
                '3840x2160 standard jpg': 300,
                '800x600 tfrecord': 2000,
                '3840x2160 tfrecord': 300
            }
        }
    }
}

DGX_A100_POD_BASELINE = {
    'systems': {
        '1': {
            'bandwidth': {
                # FIO BW speed in bytes/second
                'read': 2250000000,
                'write': 875000000
            },
            'iops': {
                # FIO IOPS speed in ops/second
                'read': 87500,
                'write': 16250
            },
            'nccl': {
                # NCCL maximum bus bandwidth in GB/s
                'max_bus_bw': 230
            },
            'dali': {
                # DALI average speed in images/second
                '800x600 standard jpg': 2000,
                '3840x2160 standard jpg': 1000,
                '800x600 tfrecord': 4000,
                '3840x2160 tfrecord': 1000
            }
        },
        '2': {
            'bandwidth': {
                # FIO BW speed in bytes/second
                'read': 4500000000,
                'write': 1750000000
            },
            'iops': {
                # FIO IOPS speed in ops/second
                'read': 175000,
                'write': 32500
            },
            'nccl': {
                # NCCL maximum bus bandwidth in GB/s
                'max_bus_bw': 180
            },
            'dali': {
                # DALI average speed in images/second
                '800x600 standard jpg': 4000,
                '3840x2160 standard jpg': 2000,
                '800x600 tfrecord': 8000,
                '3840x2160 tfrecord': 2000
            }
        },
        '3': {
            'bandwidth': {
                # FIO BW speed in bytes/second
                'read': 6750000000,
                'write': 2625000000
            },
            'iops': {
                # FIO IOPS speed in ops/second
                'read': 262500,
                'write': 48750
            },
            'nccl': {
                # NCCL maximum bus bandwidth in GB/s
                'max_bus_bw': 180
            },
            'dali': {
                # DALI average speed in images/second
                '800x600 standard jpg': 6000,
                '3840x2160 standard jpg': 3000,
                '800x600 tfrecord': 12000,
                '3840x2160 tfrecord': 3000
            }
        },
        '4': {
            'bandwidth': {
                # FIO BW speed in bytes/second
                'read': 9000000000,
                'write': 3500000000
            },
            'iops': {
                # FIO IOPS speed in ops/second
                'read': 350000,
                'write': 65000
            },
            'nccl': {
                # NCCL maximum bus bandwidth in GB/s
                'max_bus_bw': 180
            },
            'dali': {
                # DALI average speed in images/second
                '800x600 standard jpg': 8000,
                '3840x2160 standard jpg': 4000,
                '800x600 tfrecord': 16000,
                '3840x2160 tfrecord': 4000
            }
        },
        '5': {
            'bandwidth': {
                # FIO BW speed in bytes/second
                'read': 11250000000,
                'write': 4375000000
            },
            'iops': {
                # FIO IOPS speed in ops/second
                'read': 437500,
                'write': 81250
            },
            'nccl': {
                # NCCL maximum bus bandwidth in GB/s
                'max_bus_bw': 180
            },
            'dali': {
                # DALI average speed in images/second
                '800x600 standard jpg': 20000,
                '3840x2160 standard jpg': 5000,
                '800x600 tfrecord': 20000,
                '3840x2160 tfrecord': 5000
            }
        },
        '6': {
            'bandwidth': {
                # FIO BW speed in bytes/second
                'read': 13500000000,
                'write': 5250000000
            },
            'iops': {
                # FIO IOPS speed in ops/second
                'read': 525000,
                'write': 97500
            },
            'nccl': {
                # NCCL maximum bus bandwidth in GB/s
                'max_bus_bw': 180
            },
            'dali': {
                # DALI average speed in images/second
                '800x600 standard jpg': 24000,
                '3840x2160 standard jpg': 6000,
                '800x600 tfrecord': 24000,
                '3840x2160 tfrecord': 6000
            }
        },
        '7': {
            'bandwidth': {
                # FIO BW speed in bytes/second
                'read': 15750000000,
                'write': 6125000000
            },
            'iops': {
                # FIO IOPS speed in ops/second
                'read': 612500,
                'write': 113750
            },
            'nccl': {
                # NCCL maximum bus bandwidth in GB/s
                'max_bus_bw': 180
            },
            'dali': {
                # DALI average speed in images/second
                '800x600 standard jpg': 28000,
                '3840x2160 standard jpg': 7000,
                '800x600 tfrecord': 28000,
                '3840x2160 tfrecord': 7000
            }
        },
        '8': {
            'bandwidth': {
                # FIO BW speed in bytes/second
                'read': 18000000000,
                'write': 7000000000
            },
            'iops': {
                # FIO IOPS speed in ops/second
                'read': 700000,
                'write': 130000
            },
            'nccl': {
                # NCCL maximum bus bandwidth in GB/s
                'max_bus_bw': 180
            },
            'dali': {
                # DALI average speed in images/second
                '800x600 standard jpg': 32000,
                '3840x2160 standard jpg': 8000,
                '800x600 tfrecord': 32000,
                '3840x2160 tfrecord': 8000
            }
        }
    }
}

BASELINES = {
    'single-dgx-station-baseline': SINGLE_DGX_STATION_BASELINE,
    'dgx-a100-pod-baseline': DGX_A100_POD_BASELINE
}
