# SPDX-License-Identifier: MIT
# This file contains a list of exit codes for debugging
SUCCESS = 0  # Successful termination
BASELINE_FAILURE = -10  # Performance did not meet criteria
MISSING_LOG_FILES = -20  # Parsing directory with no logs
DOCKER_BUILD_FAILURE = -30  # Failure building Docker image
