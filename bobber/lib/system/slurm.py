# SPDX-License-Identifier: MIT
import os
import subprocess
import sys
from argparse import Namespace
from bobber.lib.exit_codes import SBATCH_CALL_ERROR, SLURM_QUEUE_ERROR
from typing import NoReturn


def _slurm_scripts_path() -> str:
    """
    Find the absolute path to the slurm_scripts directory.

    The slurm_scripts directory contains several *.sub files which are required
    to launch test commands via SLURM. Depending on how and where Bobber is
    installed on a system, the absolute path to this directory may change, but
    the relative path is easy to find compared to this module. By allowing
    Python to determine the absolute path to this module, the absolute path to
    slurm_scripts can be found by combining the absolute path of this module
    and the relative path to the slurm_scripts directory.

    Returns
    -------
    str
        Returns a ``string`` of the absolute path to the slurm_scripts
        directory.
    """
    directory = os.path.dirname(os.path.realpath(__file__))
    directory = os.path.join(directory, '../../slurm_scripts')
    return directory


def _sbatch_path() -> str:
    """
    Find the full path to the sbatch script.

    While launching a Python process without "shell=True" as is done for the
    test commands below, the "sbatch" command is not available as Python
    launches a new process without a proper PATH variable. Running "which
    sbatch" with a shell instance provides the full path to sbatch which can
    later be used directly to invoke the script directly instead of using the
    alias. If sbatch is not installed on the system, the application will exit.

    Returns
    -------
    str
        Returns a ``string`` of the full local path to the sbatch script.
    """
    result = subprocess.run('which sbatch', capture_output=True, shell=True)
    if not result.stderr and result.stdout:
        return str(result.stdout.strip().decode('ascii'))
    else:
        print('sbatch command not found. Please ensure SLURM is installed and '
              'functional.')
        sys.exit(SBATCH_CALL_ERROR)


def run_nccl(args: Namespace, version: str) -> NoReturn:
    """
    Launch a multi-node NCCL test via SLURM.

    Launch a NCCL test for N-nodes managed by a SLURM cluster. Multiple tests
    are queued-up as sbatch commands which will only launch once the previous
    test has completed.

    Parameters
    ----------
    args : Namespace
        A ``Namespace`` of all settings specified by the user for the test.
    version : str
        A ``string`` of the Bobber version.
    """
    # Update the version to be used in filenames
    version_underscore = version.replace('.', '_')
    # If not sweeping, set the range of nodes from N-hosts to N-hosts for a
    # single iteration of tests.
    lower_bound = args.hosts
    if args.sweep:
        lower_bound = 1
    for hosts in range(lower_bound, args.hosts + 1):
        for iteration in range(1, args.iterations + 1):
            nccl_log = os.path.join(args.log_path,
                                    f'nccl_iteration_{iteration}_'
                                    f'gpus_{args.gpus}_'
                                    f'nccl_max_{args.nccl_max}_'
                                    f'gid_{args.compute_gid}_'
                                    f'nccl_tc_{args.nccl_tc}_'
                                    f'systems_{hosts}_'
                                    f'version_{version_underscore}.log')
            nccl_path = os.path.join(_slurm_scripts_path(), 'nccl.sub')
            sbatch = _sbatch_path()
            env = {
                'HOSTS': str(hosts),
                'FS_PATH': args.storage_path,
                'CONT_VERSION': f'nvcr.io/nvidian/bobber:{version}',
                'NCCL_MAX': str(args.nccl_max),
                'LOGDIR': args.log_path,
                'LOGPATH': nccl_log,
                'NCCL_IB_HCAS': args.nccl_ib_hcas,
                'COMPUTE_GID': str(args.compute_gid),
                'NCCL_TC': args.nccl_tc or ''
            }
            cmd = [f'{sbatch}',
                   '-N',
                   f'{hosts}',
                   f'--gpus-per-node={args.gpus}',
                   '--wait',
                   '--dependency=singleton',
                   f'{nccl_path}']
            try:
                print('Running:', cmd)
                subprocess.Popen(cmd, env=env)
            except subprocess.CalledProcessError:
                print('Error queueing SLURM job for NCCL tests. '
                      'See output for errors.')
                sys.exit(SLURM_QUEUE_ERROR)


def run_dali(args: Namespace, version: str) -> NoReturn:
    """
    Launch a multi-node DALI test via SLURM.

    Launch a DALI test for N-nodes managed by a SLURM cluster. Multiple tests
    are queued-up as sbatch commands which will only launch once the previous
    test has completed.

    Parameters
    ----------
    args : Namespace
        A ``Namespace`` of all settings specified by the user for the test.
    version : str
        A ``string`` of the Bobber version.
    """
    # Update the version to be used in filenames
    version_underscore = version.replace('.', '_')
    # If not sweeping, set the range of nodes from N-hosts to N-hosts for a
    # single iteration of tests.
    lower_bound = args.hosts
    if args.sweep:
        lower_bound = 1
    for hosts in range(lower_bound, args.hosts + 1):
        for iteration in range(1, args.iterations + 1):
            dali_log = os.path.join(args.log_path,
                                    f'dali_iteration_{iteration}_'
                                    f'gpus_{args.gpus}_'
                                    f'batch_size_lg_{args.batch_size_lg}_'
                                    f'batch_size_sm_{args.batch_size_sm}_'
                                    f'systems_{hosts}_'
                                    f'version_{version_underscore}.log')
            dali_path = os.path.join(_slurm_scripts_path(), 'dali.sub')
            sbatch = _sbatch_path()
            env = {
                'HOSTS': str(hosts),
                'FS_PATH': args.storage_path,
                'CONT_VERSION': f'nvcr.io/nvidian/bobber:{version}',
                'GPUS': str(args.gpus),
                'LOGDIR': args.log_path,
                'LOGPATH': dali_log,
                'BATCH_SIZE_SM': str(args.batch_size_sm),
                'BATCH_SIZE_LG': str(args.batch_size_lg)
            }
            cmd = [f'{sbatch}',
                   '-N',
                   f'{hosts}',
                   f'--gpus-per-node={args.gpus}',
                   '--wait',
                   '--dependency=singleton',
                   f'{dali_path}']
            try:
                print('Running:', cmd)
                subprocess.Popen(cmd, env=env)
            except subprocess.CalledProcessError:
                print('Error queueing SLURM job for DALI tests. '
                      'See output for errors.')
                sys.exit(SLURM_QUEUE_ERROR)


def run_meta(args: Namespace, version: str) -> NoReturn:
    """
    Launch a multi-node metadata test via SLURM.

    Launch a metadata test for N-nodes managed by a SLURM cluster. Multiple
    tests are queued-up as sbatch commands which will only launch once the
    previous test has completed.

    Parameters
    ----------
    args : Namespace
        A ``Namespace`` of all settings specified by the user for the test.
    version : str
        A ``string`` of the Bobber version.
    """
    # Update the version to be used in filenames
    version_underscore = version.replace('.', '_')
    # If not sweeping, set the range of nodes from N-hosts to N-hosts for a
    # single iteration of tests.
    lower_bound = args.hosts
    if args.sweep:
        lower_bound = 1
    for hosts in range(lower_bound, args.hosts + 1):
        for iteration in range(1, args.iterations + 1):
            meta_log = os.path.join(args.log_path,
                                    f'stg_meta_iteration_{iteration}_'
                                    f'systems_{hosts}_'
                                    f'version_{version_underscore}.log')
            meta_path = os.path.join(_slurm_scripts_path(), 'mdtest.sub')
            sbatch = _sbatch_path()
            env = {
                'HOSTS': str(hosts),
                'FS_PATH': args.storage_path,
                'CONT_VERSION': f'nvcr.io/nvidian/bobber:{version}',
                'GPUS': str(args.gpus),
                'LOGDIR': args.log_path,
                'LOGPATH': meta_log
            }
            cmd = [f'{sbatch}',
                   '-N',
                   f'{hosts}',
                   '--wait',
                   '--dependency=singleton',
                   f'{meta_path}']
            try:
                print('Running:', cmd)
                subprocess.Popen(cmd, env=env)
            except subprocess.CalledProcessError:
                print('Error queueing SLURM job for metadata tests. '
                      'See output for errors.')
                sys.exit(SLURM_QUEUE_ERROR)
