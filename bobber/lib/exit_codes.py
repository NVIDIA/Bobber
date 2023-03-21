# SPDX-License-Identifier: MIT
# This file contains a list of exit codes for debugging
SUCCESS = 0  # Successful termination
BASELINE_FAILURE = 10  # Performance did not meet criteria
MISSING_LOG_FILES = 20  # Parsing directory with no logs
DOCKER_BUILD_FAILURE = 30  # Failure building Docker image
DOCKER_COMMUNICATION_ERROR = 31  # Unable to communicate with Docker
CONTAINER_NOT_RUNNING = 32  # Bobber container not running
NVIDIA_RUNTIME_ERROR = 33  # NVIDIA container runtime not found
CONTAINER_VERSION_MISMATCH = 34  # Container different from application
SLURM_QUEUE_ERROR = 40  # Error queueing a SLURM job
SBATCH_CALL_ERROR = 41  # Error running sbatch
