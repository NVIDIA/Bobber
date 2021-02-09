# SPDX-License-Identifier: MIT
BUILD = 'build'
EXPORT = 'export'
CAST = 'cast'
LOAD = 'load'
PARSE_RESULTS = 'parse-results'
RUN_ALL = 'run-all'
RUN_STRESS = 'run-stress'
RUN_DALI = 'run-dali'
RUN_NCCL = 'run-nccl'
RUN_NETWORKING = 'run-networking'
RUN_STG_BW = 'run-stg-bw'
RUN_STG_IOPS = 'run-stg-iops'
RUN_STG_META = 'run-stg-meta'
RUN_STG_FILL = 'run-stg-fill'

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

BASELINES = {
    'single-dgx-station-baseline': SINGLE_DGX_STATION_BASELINE
}
