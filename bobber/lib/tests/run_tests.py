# SPDX-License-Identifier: MIT
import os
from argparse import Namespace
from bobber.lib.constants import (
    RUN_ALL,
    RUN_DALI,
    RUN_NCCL,
    RUN_STG_BW,
    RUN_STG_IOPS,
    RUN_STG_125K,
    RUN_STG_META
)
from bobber.lib.docker import manager
from time import sleep
from typing import NoReturn


def run_dali(args: Namespace, bobber_version: str, iteration: int,
             hosts: str) -> NoReturn:
    """
    Run single or multi-node DALI tests.

    Run a single or multi-node DALI test which reads random image data in from
    designated storage and loads it onto local resources after preprocessing
    that is typically done for ResNet50 pipelines.

    Parameters
    ----------
    args : Namespace
        A ``Namespace`` of all settings specified by the user for the test.
    bobber_version : string
        A ``string`` of the local version of Bobber, such as '5.0.0'.
    iteration : int
        An ``int`` of the local test number, starting at 1.
    hosts : string
        A comma-separated list of hostnames to test against, such as
        'host1,host2,host3,host4'.
    """
    dali_log = os.path.join(args.log_path,
                            f'dali_iteration_{iteration}_'
                            f'gpus_{args.gpus}_'
                            f'batch_size_lg_{args.batch_size_lg}_'
                            f'batch_size_sm_{args.batch_size_sm}_'
                            f'systems_{len(hosts.split(","))}_'
                            f'version_{bobber_version}.log')
    environment = {
        'BATCH_SIZE_LG': args.batch_size_lg,
        'BATCH_SIZE_SM': args.batch_size_sm,
        'GPUS': args.gpus,
        'HOSTS': hosts,
        'SSH_IFACE': args.ssh_iface
    }
    manager.execute('tests/dali_multi.sh',
                    environment=environment,
                    log_file=dali_log)

    if args.pause > 0:
        sleep(args.pause)


def run_stg_bw(args: Namespace, bobber_version: str, iteration: int,
               hosts: str) -> NoReturn:
    """
    Run single or multi-node storage bandwidth tests with FIO.

    Run a single or multi-node storage bandwidth test with FIO which first
    writes data to the filesystem with 1MB block size and 4GB file size,
    followed by reading the data back.

    Parameters
    ----------
    args : Namespace
        A ``Namespace`` of all settings specified by the user for the test.
    bobber_version : string
        A ``string`` of the local version of Bobber, such as '5.0.0'.
    iteration : int
        An ``int`` of the local test number, starting at 1.
    hosts : string
        A comma-separated list of hostnames to test against, such as
        'host1,host2,host3,host4'.
    """
    stg_bw_log = os.path.join(args.log_path,
                              f'stg_bw_iteration_{iteration}_'
                              f'threads_{args.bw_threads}_'
                              f'direct_{args.direct}_'
                              f'depth_{args.io_depth}_'
                              f'read_pattern_{args.read_pattern}_'
                              f'write_pattern_{args.write_pattern}_'
                              f'systems_{len(hosts.split(","))}_'
                              f'version_{bobber_version}.log')
    environment = {
        'EXTRA_FLAGS': args.stg_extra_flags,
        'IO_DEPTH': args.io_depth,
        'DIRECTIO': args.direct,
        'THREADS': args.bw_threads,
        'READ_PATTERN': args.read_pattern,
        'WRITE_PATTERN': args.write_pattern,
        'HOSTS': hosts
    }
    manager.execute('tests/fio_multi.sh',
                    environment=environment,
                    log_file=stg_bw_log)

    if args.pause > 0:
        sleep(args.pause)


def run_stg_125k(args: Namespace, bobber_version: str, iteration: int,
                 hosts: str) -> NoReturn:
    """
    Run single or multi-node storage 125KB IO size tests with FIO.

    Run a single or multi-node storage bandwidth test with FIO which first
    writes data to the filesystem with 125KB block size and 4GB file size,
    followed by reading the data back.

    Parameters
    ----------
    args : Namespace
        A ``Namespace`` of all settings specified by the user for the test.
    bobber_version : string
        A ``string`` of the local version of Bobber, such as '5.0.0'.
    iteration : int
        An ``int`` of the local test number, starting at 1.
    hosts : string
        A comma-separated list of hostnames to test against, such as
        'host1,host2,host3,host4'.
    """
    stg_125k_log = os.path.join(args.log_path,
                                f'stg_125k_iteration_{iteration}_'
                                f'threads_{args.stg_125k_threads}_'
                                f'direct_{args.direct}_'
                                f'depth_{args.io_depth}_'
                                f'systems_{len(hosts.split(","))}_'
                                f'version_{bobber_version}.log')
    environment = {
        'EXTRA_FLAGS': args.stg_extra_flags,
        'IO_DEPTH': args.io_depth,
        'IOSIZE': 125,
        'DIRECTIO': args.direct,
        'THREADS': args.stg_125k_threads,
        'READ_PATTERN': args.read_pattern,
        'WRITE_PATTERN': args.write_pattern,
        'HOSTS': hosts
    }
    manager.execute('tests/fio_multi.sh',
                    environment=environment,
                    log_file=stg_125k_log)

    if args.pause > 0:
        sleep(args.pause)


def run_stg_iops(args: Namespace, bobber_version: str, iteration: int,
                 hosts: str) -> NoReturn:
    """
    Run single or multi-node storage IOPS tests with FIO.

    Run a single or multi-node storage IOPS test with FIO which first writes
    data to the filesystem with 4kB block size and 4GB file size, followed by
    reading the data back.

    Parameters
    ----------
    args : Namespace
        A ``Namespace`` of all settings specified by the user for the test.
    bobber_version : string
        A ``string`` of the local version of Bobber, such as '5.0.0'.
    iteration : int
        An ``int`` of the local test number, starting at 1.
    hosts : string
        A comma-separated list of hostnames to test against, such as
        'host1,host2,host3,host4'.
    """
    stg_iops_log = os.path.join(args.log_path,
                                f'stg_iops_iteration_{iteration}_'
                                f'threads_{args.iops_threads}_'
                                f'direct_{args.direct}_'
                                f'depth_{args.io_depth}_'
                                f'read_pattern_{args.read_pattern}_'
                                f'write_pattern_{args.write_pattern}_'
                                f'systems_{len(hosts.split(","))}_'
                                f'version_{bobber_version}.log')
    environment = {
        'EXTRA_FLAGS': args.stg_extra_flags,
        'IO_DEPTH': args.io_depth,
        'DIRECTIO': args.direct,
        'THREADS': args.iops_threads,
        'IOSIZE': 4,
        'READ_PATTERN': args.read_pattern,
        'WRITE_PATTERN': args.write_pattern,
        'HOSTS': hosts
    }
    manager.execute('tests/fio_multi.sh',
                    environment=environment,
                    log_file=stg_iops_log)

    if args.pause > 0:
        sleep(args.pause)


def run_stg_meta(args: Namespace, bobber_version: str, iteration: int,
                 hosts: str) -> NoReturn:
    """
    Run single or multi-node storage metadata test with FIO.

    Run a single or multi-node storage metadata test with FIO which tests
    various metadata operation performance for the filesystem.

    Parameters
    ----------
    args : Namespace
        A ``Namespace`` of all settings specified by the user for the test.
    bobber_version : string
        A ``string`` of the local version of Bobber, such as '5.0.0'.
    iteration : int
        An ``int`` of the local test number, starting at 1.
    hosts : string
        A comma-separated list of hostnames to test against, such as
        'host1,host2,host3,host4'.
    """
    stg_meta_log = os.path.join(args.log_path,
                                f'stg_meta_iteration_{iteration}_'
                                f'systems_{len(hosts.split(","))}_'
                                f'version_{bobber_version}.log')
    environment = {
        'HOSTS': hosts,
        'SSH_IFACE': args.ssh_iface,
        'NCCL_IB_HCAS': args.nccl_ib_hcas
    }
    manager.execute('tests/mdtest_multi.sh',
                    environment=environment,
                    log_file=stg_meta_log)

    if args.pause > 0:
        sleep(args.pause)


def run_nccl(args: Namespace, bobber_version: str, iteration: int,
             hosts: str) -> NoReturn:
    """
    Run single or multi-node NCCL test.

    Run a single or multi-node NCCL test which verifies network and GPU
    performance and communication.

    Parameters
    ----------
    args : Namespace
        A ``Namespace`` of all settings specified by the user for the test.
    bobber_version : string
        A ``string`` of the local version of Bobber, such as '5.0.0'.
    iteration : int
        An ``int`` of the local test number, starting at 1.
    hosts : string
        A comma-separated list of hostnames to test against, such as
        'host1,host2,host3,host4'.
    """
    nccl_log = os.path.join(args.log_path,
                            f'nccl_iteration_{iteration}_'
                            f'gpus_{args.gpus}_'
                            f'nccl_max_{args.nccl_max}_'
                            f'gid_{args.compute_gid}_'
                            f'nccl_tc_{args.nccl_tc}_'
                            f'systems_{len(hosts.split(","))}_'
                            f'version_{bobber_version}.log')
    environment = {
        'GPUS': args.gpus,
        'NCCL_MAX': args.nccl_max,
        'NCCL_TC': args.nccl_tc,
        'COMPUTE_GID': args.compute_gid,
        'HOSTS': hosts,
        'SSH_IFACE': args.ssh_iface,
        'NCCL_IB_HCAS': args.nccl_ib_hcas
    }
    manager.execute('tests/nccl_multi.sh',
                    environment=environment,
                    log_file=nccl_log)

    if args.pause > 0:
        sleep(args.pause)


def kickoff_test(args: Namespace, bobber_version: str, iteration: int,
                 hosts: str) -> NoReturn:
    """
    Start a specified test.

    Launch a test as requested from the CLI for the given iteration.

    Parameters
    ----------
    args : Namespace
        A ``Namespace`` of all settings specified by the user for the test.
    bobber_version : string
        A ``string`` of the local version of Bobber, such as '5.0.0'.
    iteration : int
        An ``int`` of the local test number, starting at 1.
    hosts : string
        A comma-separated list of hostnames to test against, such as
        'host1,host2,host3,host4'.
    """
    if args.command == RUN_DALI:
        run_dali(args, bobber_version, iteration, hosts)
    elif args.command == RUN_NCCL:
        run_nccl(args, bobber_version, iteration, hosts)
    elif args.command == RUN_STG_BW:
        run_stg_bw(args, bobber_version, iteration, hosts)
    elif args.command == RUN_STG_IOPS:
        run_stg_iops(args, bobber_version, iteration, hosts)
    elif args.command == RUN_STG_125K:
        run_stg_125k(args, bobber_version, iteration, hosts)
    elif args.command == RUN_STG_META:
        run_stg_meta(args, bobber_version, iteration, hosts)
    elif args.command == RUN_ALL:
        run_nccl(args, bobber_version, iteration, hosts)
        run_stg_meta(args, bobber_version, iteration, hosts)
        run_stg_bw(args, bobber_version, iteration, hosts)
        run_dali(args, bobber_version, iteration, hosts)
        run_stg_iops(args, bobber_version, iteration, hosts)
        run_stg_125k(args, bobber_version, iteration, hosts)


def test_selector(args: Namespace, bobber_version: str) -> NoReturn:
    """
    Start a test iteration.

    If the user requested to run a sweep of the hosts, the tests will begin
    with the first node in the hosts list for a single-node test, then
    progressively add the next host in the list until all nodes are tested
    together. During each iteration, one run of each requested test will be
    executed before going to the next iteration.

    Parameters
    ----------
    args : Namespace
        A ``Namespace`` of all settings specified by the user for the test.
    bobber_version : string
        A ``string`` of the local version of Bobber, such as '5.0.0'.
    """
    if args.sweep:
        hosts = []

        for host in args.hosts.split(','):
            hosts.append(host)
            for iteration in range(1, args.iterations + 1):
                host_string = ','.join(hosts)
                kickoff_test(args, bobber_version, iteration, host_string)
    else:
        for iteration in range(1, args.iterations + 1):
            kickoff_test(args, bobber_version, iteration, args.hosts)
