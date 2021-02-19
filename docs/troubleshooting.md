# Troubleshooting
Things don't always go as planned. This guide provides some steps to
troubleshoot Bobber when it doesn't work as expected.

## General troubleshooting
The first item to check when something goes wrong is the Docker image and
containers across the cluster. On all hosts, verify the Docker image is built
and matches the version of the Bobber wheel. Check the Bobber version with:

```
$ bobber --version
6.1.1
```

The version number is listed in the first line. Check the Bobber image is built
and matches the version above with:

```
$ docker images | grep nvidia/bobber
nvidia/bobber   6.1.1   c697a75ee482    36 minutes ago  12.4GB
```

If the above command does not contain output or the second column (`6.1.1` in
the example) does not match the version of Bobber from the first step, the image
needs to be built. Run `bobber build` to build the image and verify using the
steps above once complete.

Before any tests can be run, the container needs to be launched on all nodes.
This can be verified with:

```
$ docker ps | grep bobber
1ab2b10f8eb1    nvidia/bobber:6.1.1 "/usr/local/bin/nvid..."    4 days ago  Up 4 days   bobber
```

If the above command does not contain output, the container needs to be launched
using the `bobber cast /path/to/storage` command.

## Exit codes
When the application terminates after a handled issue, various exit codes may be
thrown depending on the situation. The following list provides extra context on
these codes:

  * `0`: Exit Success - The application terminated successfully.
  * `-10`: Baseline Failure - This is thrown while comparing results from a test run against a baseline (either one of the defaults or a custom baseline) using the `bobber parse-results --compare-baseline ...` or `bobber parse-results --custom-baseline ...` command. If at least one result doesn't exceed the baseline performance, it will be marked as a failure. Check the output of the command for a list of the results that don't exceed baseline performance and verify connectivity and configuration.
  * `-20`: Missing Log Files - Thrown while attempting to parse results while specifying a directory that does not contain valid log files. Verify the directory being parsed contains log files with data.
  * `-30`: Docker Build Failure - Thrown while trying to build the Bobber image with `bobber build`. Look at the output from the command to see if there are any specific issues while building. This is commonly seen when networking on host and/or Docker levels are down.
