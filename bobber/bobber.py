# SPDX-License-Identifier: MIT
import bobber.lib.docker
import json
from argparse import ArgumentParser, Namespace
from copy import copy
from bobber import __version__
from bobber.lib.constants import (
    BASELINES,
    BUILD,
    DGX_2,
    DGX_A100_DUAL,
    DGX_A100_SINGLE,
    EXPORT,
    CAST,
    LOAD,
    PARSE_RESULTS,
    RUN_ALL,
    RUN_STRESS,
    RUN_DALI,
    RUN_NCCL,
    RUN_NETWORKING,
    RUN_STG_BW,
    RUN_STG_IOPS,
    RUN_STG_META,
    RUN_STG_FILL,
    SYSTEMS
)
from bobber.lib.analysis import parse_results
from bobber.lib.system.file_handler import create_directory
from bobber.lib.tests import run_tests
from typing import NoReturn


def parse_args(version: str) -> Namespace:
    """
    Parse arguments passed to the application.

    A custom argument parser handles multiple commands and options to launch
    the desired function.

    Parameters
    ----------
    version : string
        A ``string`` of the Bobber version.

    Returns
    -------
    Namespace
        Returns a ``Namespace`` of all of the arguments that were parsed from
        the application during runtime.
    """
    parser = ArgumentParser(f'Bobber Version: {version}')
    # Required positional command subparser which should be specified first
    commands = parser.add_subparsers(dest='command', metavar='command')
    commands_parent = ArgumentParser(add_help=False)

    # More general options which apply to a majority of the running commands
    # Note that all arguments prepended with '--' are optional
    commands_parent.add_argument('log_path', metavar='log-path', help='Path '
                                 'used to store log files on the head node')
    commands_parent.add_argument('hosts', help='Comma-separated list of '
                                 'hostnames or IP addresses')
    commands_parent.add_argument('--config-path', help='Read a JSON config '
                                 'file with expected parameters and use those '
                                 'values for testing. Ignores all other '
                                 'optional flags')
    commands_parent.add_argument('--gpus', help='Number of GPUs contained '
                                 'within a system or systems under test '
                                 '(heterogeneous counts not supported)',
                                 type=int)
    commands_parent.add_argument('--compute-gid', help='The compute gid. '
                                 'defaults to 0 - check with "show_gids" '
                                 'command. A non-default gid is needed for '
                                 'Ethernet (frequently gid 3)', type=int,
                                 default=0)
    commands_parent.add_argument('--nccl-tc', help='NCCL setting required to '
                                 'use prio3 traffic for Ethernet. Set to 106 '
                                 'for Ethernet, and do not set for IB.',
                                 type=int)
    commands_parent.add_argument('--batch-size-sm', help='Batch size to use '
                                 'with DALI data ingest tests for small '
                                 'images', type=int)
    commands_parent.add_argument('--batch-size-lg', help='Batch size to use '
                                 'with DALI data ingest tests for large '
                                 'images', type=int)
    commands_parent.add_argument('--nccl-max', help='Specify the maximum data '
                                 'size to test with NCCL, in Gigabytes '
                                 '(default is 1 GB)', type=int, default=1)
    commands_parent.add_argument('--nccl-ib-hcas', help='Specify the list of '
                                 'interfaces to use for NCCL test multinode '
                                 'communication', default='')
    commands_parent.add_argument('--ssh-iface', help='Specify ssh interface '
                                 'for the system(s) under test ', default='')
    commands_parent.add_argument('--no-direct', help='Disable running with '
                                 'direct IO for applications that support it',
                                 action='store_true')
    commands_parent.add_argument('--io-depth', help='Customize the IO depth '
                                 'for direct IO testing', type=int, default=16)
    commands_parent.add_argument('--bw-threads', help='Maximum number of '
                                 'threads to use for bandwidth tests',
                                 type=int)
    commands_parent.add_argument('--iops-threads', help='Maximum number of '
                                 'threads to use for iops tests', type=int)
    commands_parent.add_argument('--iterations', help='Number of iterations to'
                                 ' execute per test - a seperate log file will'
                                 ' be generated for each iteration', type=int,
                                 default=10)
    commands_parent.add_argument('--sweep', help='If present, will run all '
                                 'tests for all specified iterations from a '
                                 'single system to the number of systems '
                                 'specified in the --hosts flag, with a step '
                                 'of a single system (so, 3 systems specified '
                                 'would result in tests for 1, 2, and 3 '
                                 'systems)', action='store_true')
    commands_parent.add_argument('--system', help='If system is specified, '
                                 'iops-threads, bw-threads, gpus, batch size, '
                                 'and network interface names are given '
                                 'default values - override by specifying the '
                                 'flags you\'d prefer to override, ignore the '
                                 'flags you are ok with using defaults for '
                                 'supported systems: dgx-a100-single, '
                                 'dgx-a100-dual, and dgx-2 for now. -single '
                                 'is used for a system with a single storage '
                                 'NIC, and -dual is used for a system with two'
                                 ' storage NICs', choices=SYSTEMS.keys())
    commands_parent.add_argument('--stg-extra-flags', help='Experimental - '
                                 'add extra flags to stg tests (currently '
                                 'supported - stg-bw and stg-iops). If '
                                 'providing more than one flag, wrap entire '
                                 'set in quotes')

    # Create the test initiation commands with the general options above
    commands.add_parser(RUN_ALL, help='Run all tests',
                        parents=[commands_parent])
    commands.add_parser(RUN_STRESS, help='Run NVSM stress test only',
                        parents=[commands_parent])
    commands.add_parser(RUN_DALI, help='Run DALI tests only',
                        parents=[commands_parent])
    commands.add_parser(RUN_NCCL, help='Run NCCL tests only',
                        parents=[commands_parent])
    commands.add_parser(RUN_NETWORKING, help='Run networking tests only',
                        parents=[commands_parent])
    commands.add_parser(RUN_STG_BW, help='Run storage bandwdith tests only',
                        parents=[commands_parent])
    commands.add_parser(RUN_STG_IOPS, help='Run storage IOPS tests only',
                        parents=[commands_parent])
    commands.add_parser(RUN_STG_META, help='Run storage metadata tests only',
                        parents=[commands_parent])
    commands.add_parser(RUN_STG_FILL, help='Run storage fill workload - '
                        'intended to run only from a single client, will '
                        'ignore --hosts argument')

    # Options specific to exporting the containers
    export = commands.add_parser(EXPORT, help='Export the container for '
                                 'multisystem tests')

    # Options specific to parsing the results
    parse = commands.add_parser(PARSE_RESULTS, help='Parse and display results'
                                'from the log files')
    parse.add_argument('log_path', metavar='log-path', help='Path to saved '
                       'logfile location')
    parse.add_argument('--json-filename', help='Specify the filename to use '
                       'for saving the JSON data. Defaults to the current '
                       'timestamp.', default=None)
    parse.add_argument('--override-version-check', help='Optionally skip the '
                       'version check to ensure the same version of Bobber '
                       'was used for all tests.', action='store_true')
    parse.add_argument('--compare-baseline', help='Compare the values produced'
                       ' by a test run against a pre-defined baseline to '
                       'verify performance meets an acceptable threshold.',
                       choices=BASELINES)

    # Options specific to building the containers
    build = commands.add_parser(BUILD, help='Build the container')

    # Options specific to casting the containers
    cast = commands.add_parser(CAST, help='Start the container')
    cast.add_argument('storage_path', metavar='storage-path', help='Path at '
                      'which the filesystem under test is mounted')
    cast.add_argument('--ignore-gpu', help='Start the Bobber container '
                      'without GPUs', action='store_true')

    # Options specific to loading a Docker image from a local binary
    load = commands.add_parser(LOAD, help='Load a container from a local '
                               'binary')
    load.add_argument('filename', help='Filename of local *.tar file of '
                      'the image to load')
    return parser.parse_args()


def bobber_version() -> str:
    """
    Find the Bobber version.

    Read the version of Bobber from the VERSION file and return it as a
    trimmed string.

    Returns
    -------
    string
        Returns a ``string`` of the version number without any whitespace.
    """
    return __version__.strip()


def load_from_config(config_path: str) -> Namespace:
    """
    Load a JSON config file and use those values.

    If the --config-path flag is passed, the values should be read directly
    from that file and used for a new test.

    Parameters
    ----------
    config_path : string
        A ``string`` pointing to the JSON config file used during a previous
        test.

    Returns
    -------
    Namespace
        Returns a ``Namespace`` of all previous settings to use for a new test
        pass.
    """
    with open(config_path, 'r') as config:
        settings = json.loads(config.read())
        return Namespace(**settings)


def save_config(args: Namespace) -> NoReturn:
    """
    Save the settings as JSON.

    The settings should be saved in the log directory as a JSON object to allow
    a test to be reproduced later on with identical parameters.

    Parameters
    ----------
    args : Namespace
        A ``Namespace`` of all settings that are used for a test pass.
    """
    settings = vars(args)
    with open(f'{args.log_path}/command_parameters.json', 'w') as fp:
        fp.write(json.dumps(settings))


def load_settings(args: Namespace) -> Namespace:
    """
    Load default settings prior to overriding requested flags.

    If the --config-path flag is specified pointing to a JSON file with
    settings used from a previous run, all values will be read directly from
    that run and used for a new run.

    If the --config-path flag is not specified, new settings will be puled from
    the CLI. While specifying the --system flag, several default parameters are
    populated. These values need to be loaded into the args object first to
    avoid them from being lost. By reading all other values specified in the
    args object, the new arguments object should be updated. By default, the
    --system variables are used, but in case of any collisions, the values
    passed by the user are taken.

    Parameters
    ----------
    args : Namespace
        The arguments that were passed by the user from the CLI.

    Returns
    -------
    Namespace
        Returns a ``Namespace`` of the final settings to use for all flags
        based on the system defaults and the user-specified values.
    """
    if args.config_path:
        return load_from_config(args.config_path)
    # Create a copy of the arguments so they aren't lost while setting the
    # defaults from the --system flag.
    args_copy = copy(args)
    # First set the default values provided by the system.
    if args.system:
        for key, value in SYSTEMS[args.system].items():
            setattr(args_copy, key, value)
    # Capture any other arguments that were passed, and override the defaults
    # if specified.
    for arg in vars(args):
        if getattr(args, arg):
            setattr(args_copy, arg, getattr(args, arg))
    args = copy(args_copy)
    if args.no_direct:
        setattr(args, 'direct', 0)
    else:
        setattr(args, 'direct', 1)
    return args


def execute_command(args: Namespace, version: str) -> NoReturn:
    """
    Execute a specific command from Bobber.

    Call and run the command that was passed from the user via the CLI.

    Parameters
    ----------
    args : Namespace
        A ``Namespace`` of all of the flags that were passed via the CLI.
    version : string
        A ``string`` of the Bobber version.
    """
    if args.command == PARSE_RESULTS:
        parse_results.main(args.log_path, args.compare_baseline)
    elif args.command == BUILD:
        bobber.lib.docker.build(version)
    elif args.command == EXPORT:
        bobber.lib.docker.export(version)
    elif args.command == CAST:
        bobber.lib.docker.cast(args.storage_path, args.ignore_gpu, version)
    elif args.command == LOAD:
        bobber.lib.docker.load(args.filename)
    else:
        # Update the version to be used in filenames
        version_underscore = version.replace('.', '_')
        args = load_settings(args)
        create_directory(args.log_path)
        save_config(args)
        run_tests.test_selector(args, version_underscore)


def main() -> NoReturn:
    """
    Launch a test with the Bobber framework.

    Launch a number of quick benchmarks to measure single and multi-node
    performance for AI-related systems.
    """
    version = bobber_version()
    args = parse_args(version)
    execute_command(args, version)


if __name__ == "__main__":
    main()
