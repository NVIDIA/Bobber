# SPDX-License-Identifier: MIT
import docker
from bobber.lib.docker.management import DockerManager

manager = DockerManager()

# Map the instance methods to allow importing as "bobber.docker.<instance>"
# in other modules.
build = manager.build
cast = manager.cast
execute = manager.execute
export = manager.export
load = manager.load
