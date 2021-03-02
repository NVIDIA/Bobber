# SPDX-License-Identifier: MIT
import docker
import os
import sys
from bobber.__version__ import __version__ as version
from bobber.lib.exit_codes import (CONTAINER_NOT_RUNNING,
                                   CONTAINER_VERSION_MISMATCH,
                                   DOCKER_BUILD_FAILURE,
                                   DOCKER_COMMUNICATION_ERROR,
                                   NVIDIA_RUNTIME_ERROR)
from bobber.lib.system.file_handler import update_log
from docker.models.containers import Container
from typing import NoReturn, Optional


class DockerManager:
    """
    Build, launch, and execute commands for Docker containers.

    The DockerManager provides a single interface accessible from the entire
    Bobber package in which to communicate with Docker containers. The class
    provides the ability to build new containers based on the provided
    Dockerfile, launch the container with necessary settings for tests, and
    execute commands inside the launched container to run tests. An instance
    of this class is created in the bobber.lib.docker.__init__.py module which
    can be access from other modules without re-instantiating the class.
    """
    def __init__(self) -> NoReturn:
        try:
            self.client = docker.from_env()
            self.cli = docker.APIClient(timeout=600)
        except docker.errors.DockerException as e:
            if 'error while fetching server api version' in str(e).lower():
                print('Error: Could not communicate with the Docker daemon.')
                print('Ensure Docker is running with "systemctl start docker"')
                sys.exit(DOCKER_COMMUNICATION_ERROR)

    def _build_if_not_built(self, tag: str, bobber_version: str) -> NoReturn:
        """
        Build the image if not built already.

        Check if an image exists for the local version of Bobber. If not, build
        the image immediately.

        Parameters
        ----------
        tag : string
            A ``string`` of the Bobber image name, such as
            'nvidia/bobber:5.0.0'.
        bobber_version : string
            A ``string`` of the local version of Bobber, such as '5.0.0'.
        """
        try:
            self.client.images.get(tag)
        except docker.errors.ImageNotFound:
            print(f'Image {tag} not built, building now...')
            self.build(bobber_version)

    def get_tag(self, bobber_version: str) -> str:
        """
        Create the image name.

        Build the full image name including the tag, such as
        'nvidia/bobber:5.0.0'.

        Parameters
        ----------
        bobber_version : string
            A ``string`` of the local version of Bobber, such as '5.0.0'.

        Returns
        -------
        str
            Returns a ``string`` of the full image name plus tag, such as
            'nvidia/bobber:5.0.0'.
        """
        return f'nvidia/bobber:{bobber_version}'

    def cast(self, storage_path: str, ignore_gpu: bool,
             bobber_version: str) -> NoReturn:
        """
        Launch a container with necessary settings.

        Launch a Bobber image with various settings required to initiate the
        testing framework, including attaching GPUs, starting an SSH daemon,
        setting the container to privileged mode, and attaching a filesystem
        to be accessible inside the container.

        The launched container will be based off of the Bobber image for the
        current version of the application. If the image does not yet exist,
        it will be built automatically. The launched container is named
        'bobber'.

        Parameters
        ----------
        storage_path : string
            A ``string`` of the absolute path to the storage location to test
            against, such as `/mnt/storage`.
        ignore_gpu : boolean
            When `True`, launches the container without GPU resources. Defaults
            to `False`.
        bobber_version : string
            A ``string`` of the local version of Bobber, such as '5.0.0'.
        """
        tag = self.get_tag(bobber_version)
        self._build_if_not_built(tag, bobber_version)
        runtime = None
        if not ignore_gpu:
            runtime = 'nvidia'
        try:
            self.client.containers.run(
                tag,
                'bash -c "/usr/sbin/sshd; sleep infinity"',
                detach=True,
                auto_remove=True,
                ipc_mode='host',
                name='bobber',
                network_mode='host',
                privileged=True,
                shm_size='1G',
                runtime=runtime,
                ulimits=[
                    docker.types.Ulimit(name='memlock',
                                        soft=-1,
                                        hard=-1),
                    docker.types.Ulimit(name='stack',
                                        soft=67108864,
                                        hard=67108864)
                ],
                volumes={
                    f'{storage_path}': {
                        'bind': '/mnt/fs_under_test',
                        'mode': 'rw'
                    }
                }
            )
        except docker.errors.APIError as e:
            if 'Unknown runtime specified nvidia' in str(e):
                print('NVIDIA container runtime not found. Ensure the latest '
                      'nvidia-docker libraries and NVIDIA drivers are '
                      'installed.')
                sys.exit(NVIDIA_RUNTIME_ERROR)

    def export(self, bobber_version: str) -> NoReturn:
        """
        Save an image as a tarball.

        To make it easy to transfer an image to multiple machines, the image
        can be saved as a tarball which can be copied directly to a remote
        device. On the other device, run the "load" command to load the copied
        tarball.

        Parameters
        ----------
        bobber_version : string
            A ``string`` of the local version of Bobber, such as '5.0.0'.
        """
        tag = self.get_tag(bobber_version)
        self._build_if_not_built(tag, bobber_version)
        filename = tag.replace('/', '_').replace(':', '_')
        print(f'Exporting {tag} to "{filename}.tar". This may take a while...')
        image = self.cli.get_image(tag)
        with open(f'{filename}.tar', 'wb') as image_file:
            for chunk in image:
                image_file.write(chunk)
        print(f'{tag} saved to {filename}.tar')

    def build(self, bobber_version: str) -> NoReturn:
        """
        Build the image on the Dockerfile.

        Build a new image based on the Dockerfile named
        'nvidia/bobber:{version}'.

        Parameters
        ----------
        bobber_version : string
            A ``string`` of the local version of Bobber, such as '5.0.0'.
        """
        tag = self.get_tag(bobber_version)
        print('Building a new image. This may take a while...')
        # Set the path to the repository's parent directory.
        path = os.path.dirname(os.path.abspath(__file__))
        path = '/'.join(path.split('/')[:-2])
        output = self.cli.build(path=path,
                                dockerfile='lib/docker/Dockerfile',
                                tag=tag,
                                decode=True)
        for line in output:
            if 'error' in line.keys():
                print(line['error'].rstrip())
                print(f'{tag} build failed. See error above.')
                sys.exit(DOCKER_BUILD_FAILURE)
            if 'stream' in line.keys() and line['stream'].strip() != '':
                print(line['stream'].rstrip())
        print(f'{tag} successfully built')

    def load(self, filename: str) -> NoReturn:
        """
        Load a Docker image from a tarball.

        If a Bobber image was saved as a tarball using the "export" command, it
        can be loaded on the system using the "load" command.

        Parameters
        ----------
        filename : string
            A ``string`` of the filename for the local tarball to load, such as
            './nvidia_bobber_5.0.0.tar'.
        """
        print(f'Importing {filename}. This may take a while...')
        with open(filename, 'rb') as image_file:
            self.client.images.load(image_file)

    def execute(self, command: str, environment: Optional[dict] = None,
                log_file: Optional[str] = None) -> NoReturn:
        """
        Execute a command against the running container.

        Assuming the Bobber container is already launched from the "cast"
        command, execute a specific command and stream the output to the
        terminal. Optionally specify a dictionary with any necessary
        environment variables and a log file to save the output to.

        Parameters
        ----------
        command : string
            A ``string`` of the command to run inside the container.
        environment : dict (Optional)
            A ``dictionary`` of environment variables to use where the keys are
            the name of the variable and the values are the corresponding value
            to set.
        log_file : string (Optional)
            A ``string`` of the path and filename to optionally save output to.
        """
        if not self.running:
            print('Bobber container not running. Launch a container with '
                  '"bobber cast" prior to running any tests.')
            sys.exit(CONTAINER_NOT_RUNNING)
        bobber = self.client.containers.get('bobber')
        if not self.version_match(bobber):
            print('Bobber container version mismatch.')
            print('Kill the running Bobber container with "docker kill bobber"'
                  ' and re-cast a new container with "bobber cast" prior to '
                  'running any tests.')
            sys.exit(CONTAINER_VERSION_MISMATCH)
        result = bobber.exec_run(
            command,
            demux=False,
            environment=environment,
            stream=True
        )
        # Continually print STDOUT and STDERR until there is nothing left
        while True:
            try:
                output = next(result.output).decode('ascii')
                print(output.rstrip())
                if log_file:
                    update_log(log_file, output)
            # Usually only happens for terminating characters at the end of
            # streams
            except UnicodeDecodeError:
                print(result.output)
            except StopIteration:
                break

    def version_match(self, container: Container) -> bool:
        """
        Determine if the Bobber container version matches the application.

        The running Bobber container version must match the local Bobber
        application version to ensure all tests will function properly.

        Parameters
        ----------
        container : Container
            A ``Container`` object representing the running Bobber image.

        Returns
        -------
        bool
            Returns `True` when the versions match and `False` when not.
        """
        if f'nvidia/bobber:{version}' not in container.image.tags:
            return False
        return True

    @property
    def running(self) -> bool:
        """
        Determine if the Bobber container is running on the system.

        Check to see if the current version of the Bobber container is running
        on the local machine and return the status. This method can be used to
        determine whether or not to run a command that depends on the container
        being launched.

        Returns
        -------
        bool
            Returns `True` when the container is running and `False` when not.
        """
        try:
            bobber = self.client.containers.get('bobber')
        except docker.errors.NotFound:
            return False
        else:
            return True
