# SPDX-License-Identifier: MIT
import subprocess
import sys
from bobber.lib.docker import manager
from typing import NoReturn


def copy_keys(hosts: str, user: str) -> NoReturn:
    """
    Generate and copy SSH keys to all hosts.

    Launch a shell script included with the package which generates a local SSH
    key that is copied to all Bobber containers on all nodes to allow
    passwordless communication for MPI.

    Parameters
    ----------
    hosts : string
        A comma-separated list as a ``string`` representing all hosts, such as
        'host1,host2,host3,...'.
    user : string
        A ``string`` of the user to use to login to remote hosts as, if
        necessary.
    """
    if not manager.running():
        print('Bobber container is not running. Please ensure Bobber is '
              'running on all nodes using the "bobber cast" command before '
              'running "bobber sync".')
        sys.exit(-1)
    try:
        subprocess.run(['bobber/bin/sync-keys.sh', hosts, user], check=True)
    except subprocess.CalledProcessError:
        print('Error synchronizing keys. See output from the sync script '
              'above.')
        sys.exit(-1)
