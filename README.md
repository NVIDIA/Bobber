# Bobber
Containerized testing of system components that impact AI workload performance.

## System Requirements
The following requirements must be met to ensure proper functionality of Bobber:

  * Operating System: DGX OS 4.99 or newer
  * NVIDIA DGX Hardware: DGX A100, DGX 2
  * GPU Architecture: NVIDIA Ampere or Turing
  * Docker Version: 19.03 or newer
  * CUDA Version: 11.0 or newer
  * NVIDIA Driver Version: 450 or newer
  * Python Version: 3.6 or newer

While we anticipate the application to function with older/different
combinations of the OS, CUDA, and driver versions than those listed above, these
are the minimum versions that have been tested and verified to work with Bobber.
Please create an issue if there are any questions on support for different
requirements.

For more information on installing and using Docker, view the
[Docker document](docs/docker.md).

### Running on unsupported systems
Officially, Bobber supports the NVIDIA DGX A100 and DGX-2 platforms for testing,
but other Linux-based platforms with NVIDIA GPUs might also work. While running
any of the tests listed at the bottom of this document, look at the `--help`
output to see if any values need to be changed for other systems.

## Downloading the binary
Bobber features a Python wheel which can be downloaded from GitHub to easily
install the application on a range of machines. Go to the [releases](https://github.com/NVIDIA/Bobber/releases)
page on the repository and find the latest release. Look for the "Binary"
section in the release notes and copy the link to the latest wheel.

Using `wget`, download the binary using the address from the previous step to all
remote machines which will be tested, for example:

```bash
wget https://github.com/NVIDIA/Bobber/releases/download/v6.0.0/nvidia_bobber-6.0.0-py3-none-any.whl
```

## Python dependency installation
The Python wheel can be installed with PIP3 for Python3 which will also install
all required dependencies.

First, install PIP3 if not already installed on all of the machines that will be
tested:

```bash
sudo apt update
sudo apt install -y python3-pip
```

Next, install the Python wheel globally which was downloaded during the previous
step on all nodes. By installing globally with `sudo`, the application will be
available in all paths to all users.

```bash
sudo pip3 install nvidia_bobber-*-none-any.whl
```

The installation can be verified with `pip3 freeze` after completion:

```bash
$ pip3 freeze | grep bobber
nvidia-bobber==6.0.0
```

Bobber can also be verified by printing the usage statement:

```
$ bobber --help
usage: Bobber Version: 6.0.0 [-h] command ...

positional arguments:
  command
    run-all       Run all tests
    run-stress    Run NVSM stress test only
    run-dali      Run DALI tests only
    run-nccl      Run NCCL tests only
    run-networking
                  Run networking tests only
    run-stg-bw    Run storage bandwdith tests only
    run-stg-iops  Run storage IOPS tests only
    run-stg-meta  Run storage metadata tests only
    run-stg-fill  Run storage fill workload - intended to run only from a
                  single client, will ignore --hosts argument
    export        Export the container for multisystem tests
    parse-results
                  Parse and display resultsfrom the log files
    build         Build the container
    cast          Start the container
    load          Load a container from a local binary

optional arguments:
  -h, --help      show this help message and exit
```

## Build Bobber container (includes OSU Tests, NCCL Tests, fio, mdtest, DALI RN50 Pipeline, and the base NGC TensorFlow container)
The Bobber application includes a built-in mechanism to build the Docker
container where all tests will be run. This command should be run on a single
system in the cluster as it will be copied in a future step. For single-node
tests, run the command on the node to be tested.

```bash
$ bobber build
Building a new image. This may take a while...
...
nvidia/bobber:6.0.0 successfully built
```

After building, verify the image is accessible in Docker:

```bash
$ docker images | grep nvidia/bobber
nvidia/bobber               6.0.0               c697a75ee482        36 minutes ago      12.4GB
```

## Save container
Bobber relies on shared SSH keys to communicate between containers via MPI. This
is done by generating an SSH key in the image during build time and using that
same container on all hosts. This requires saving the image to a local tarball
and transferring the image to all other nodes. The `export` command saves the
image as a local tarball. Run the command on the node from the previous step
where the Docker image is located.

If running on a single node, this step is not required.

```bash
$ bobber export
Exporting nvidia/bobber:6.0.0 to "nvidia_bobber_6.0.0.tar". This may take a while...
nvidia/bobber:6.0.0 saved to nvidia_bobber_6.0.0.tar
$ ls
nvidia_bobber_6.0.0.tar
```

## Copy container to other nodes
Copy the saved container to all other nodes using `scp` (skip if only running
on a single node):

```bash
scp -r nvidia_bobber_{version}.tar user@test-machine-2:~/bobber
scp -r nvidia_bobber_{version}.tar user@test-machine-3:~/bobber
...
```

Do this for each host you intend to include in the test. A bash `for` loop to
can be used to iterate over all systems - you could also target the high
performance network to speed up the copy further (this is a 10+ GB copy). Like
so:

```bash
scp -r nvidia_bobber_{version}.tar user@test-machine-2-ib:~/bobber
...
```

Again, this is just an example - you'll need to figure out what your high speed
network addresses are on each system you intend to copy to.

## Load container on other nodes
On all other nodes, load the copied Docker image.

```bash
$ docker load < nvidia_bobber_{version}.tar
$ docker images | grep bobber
nvidia/bobber               6.0.0               c697a75ee482        36 minutes ago      12.4GB
```

## Ensure shared filesystem is mounted, if necessary
Bobber primarily tests performance for shared filesystems attached to a compute
cluster. This requires all compute nodes to be connected to the same shared
storage.

Ideally, you'll be able to execute the same mount command on each system to
mount the filesystem, but your mileage may vary. If each system uses the same
network address for mount,  use `pdsh`. If not, you'll want to ssh into each
system and mount a different address.

It is strongly suggested that you make the mount point the *same* across all
systems under test. Double check the mountpoint using the `mount` command:

```bash
test-machine-1$ mount | grep shared_filesystem
192.168.0.100:/fs   20T  1.2T   19T   6% /mnt/shared_filesystem
test-machine-2$ mount | grep shared_filesystem
192.168.0.100:/fs   20T  1.2T   19T   6% /mnt/shared_filesystem
...
```

Do note that multinode tests *expect* shared filesystem access. Tests will not
work correctly at scale if an unshared filesystem is used for multinode tests.

For single-node tests, shared storage is not required.

## Start Bobber container on each system
Prior to starting the tests, the Bobber container needs to be launched and
running on each node that will be tested. The `cast` command launches a
container with all dependencies and will listen for requests to intiate tests.

```bash
bobber cast /mnt/shared_filesystem
```

Another path with `pdsh`...  

```bash
sudo pdsh -R ssh -w test-machine-1,test-machine-2 'pushd /home/user; bobber cast /mnt/shared_filesystem'
```

To verify the container is running, use `docker ps`:

```bash
$ docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS               NAMES
317b6cf928f8        c697a75ee482        "/usr/local/bin/nvid…"   30 hours ago        Up 30 hours                             bobber
```

## Create log dir on primary test system
Pick your favorite system to designate as the head node - at this point, they
should all be usable as the primary system. Create a log directory to keep tests
collected:

```bash
mkdir -p ~/logs  
```

## Run nvsm stress test
The NVSM stress test is not one of the core Bobber tests but is recommended to
verify GPUs are running and configured properly.

```bash
sudo nvsm stress-test --force
```

This is the only one that is run on each system individually and outside of
Bobber. It verifies each system's health. You could try to run it via `pdsh`.

## Test flags
Bobber uses many flags which can vary the performance of tests. While the
default values should be sufficient for most systems, it is possible that the
settings will need to be achieve optimal performance. To view a list of flags
that can be updated, add the `--help` flag to the end of any `run-*` command in
Bobber, such as:

```bash
bobber run-all --help
```

### Pre-tuned flags
The `--system` flag allows users to specify a pre-tuned config that matches
their compute systems, if supported, such as the DGX A100 with single-port or
dual-port storage adapters, and the DGX-2. This will set values for nearly all
flags for the tests, including GPU counts, SSH interfaces, NCCL HCAs, and more.
If your system is not supported, these values will need to be specified for
proper functionality.

### Flags that will likely need to change
The flags that are most commonly updated, depending on the filesystem under
test, are as follows:

  * `--io-depth` - Ask the vendor what io depth they prefer to fio - will default to 16 if nothing else is used.  
  * `--bw-threads` - Again, ask the vendor, as this is another fio configurable. Will default to 16 if unspecified.
  * `--iops-threads` - Ask the vendor, another fio configurable. Defaults to 200 if unspecified.  

## A note on long-running tests
A full run of tests against a POD can take anywhere from a half hour to 24+
hours. In that time, your shell is likely to time out for a variety of reasons.
This will result in the test suite halting. To safeguard against this, it is
recommended to run tests in a `screen` session. Like so:

```bash
$ screen
```

Once you hit Space or Return, use the shell as you normally would - if your
session to the remote machines times out, you can ssh back into your system and
run this to get back to your session:

```bash
$ screen -r
```

## Run DALI test (EXPERIMENTAL)
Note 1: The DALI tests are under active development and are currently marked as
experimental. Expect changes to the tests in the future which could potentially
invalidate any existing results.

Note 2: `dgx-a100-single` is used for DGX A100 systems with a single storage
NIC. `dgx-a100-dual` is used for DGX A100 systems with two storage NICs.

Note 3: For the DALI test and all other tests below, use the `--system` flag
that is most appropriate for your environment, or specify flag values manually
per the "Pre-tuned flags" section above. Each command only needs to be run once.

```bash
bobber run-dali --iterations 2 --sweep --system dgx-a100-single /home/user/logs test-machine-1,test-machine-2
bobber run-dali --iterations 2 --sweep --system dgx-a100-dual /home/user/logs test-machine-1,test-machine-2
bobber run-dali --iterations 2 --sweep --system dgx-2 /home/user/logs dgx-2-1,dgx-2-2
```

## Run NCCL test
```bash
bobber run-nccl --iterations 2 --sweep --system dgx-a100-single /home/user/logs test-machine-1,test-machine-2
bobber run-nccl --iterations 2 --sweep --system dgx-a100-dual /home/user/logs test-machine-1,test-machine-2
bobber run-nccl --iterations 2 --sweep --system dgx-2 /home/user/logs dgx-2-1,dgx-2-2
```

## Run FIO Bandwidth test
```bash
bobber run-stg-bw --iterations 2 --sweep --system dgx-a100-single /home/user/logs test-machine-1,test-machine-2
bobber run-stg-bw --iterations 2 --sweep --system dgx-a100-dual /home/user/logstest-machine-1,test-machine-2
bobber run-stg-bw --iterations 2 --sweep --system dgx-2 /home/user/logs dgx-2-1,dgx-2-2
```

## Run FIO IOPS test
```bash
bobber run-stg-iops --iterations 2 --sweep --system dgx-a100-single /home/user/logs test-machine-1,test-machine-2
bobber run-stg-iops --iterations 2 --sweep --system dgx-a100-dual /home/user/logs test-machine-1,test-machine-2
bobber run-stg-iops --iterations 2 --sweep --system dgx-2 /home/user/logs dgx-2-1,dgx-2-2
```

## Run metadata test
```bash
bobber run-stg-meta --iterations 2 --sweep --system dgx-a100-single /home/user/logs test-machine-1,test-machine-2
bobber run-stg-meta --iterations 2 --sweep --system dgx-a100-dual /home/user/logs test-machine-1,test-machine-2
bobber run-stg-meta --iterations 2 --sweep --system dgx-2 /home/user/logs dgx-2-1,dgx-2-2
```

## Run 'all' tests
The `run-all` command is the go-to test which runs all of the commands above in
one shot. To run all tests in a single session, it is recommended to run this
test instead of all of the others above.

```bash
bobber run-all --iterations 2 --sweep --system dgx-a100-single /home/user/logs test-machine-1,test-machine-2
bobber run-all --iterations 2 --sweep --system dgx-a100-dual /home/user/logs test-machine-1,test-machine-2
bobber run-all --iterations 2 --sweep --system dgx-2 /home/user/logs dgx-2-1,dgx-2-2
```

## Running from previous config
All Bobber runs generate a JSON file which captures all commands used for the
tests and saves it to the log path. This JSON file can be used as a basis for
future tests to repeat work. To read from the config file, specify the full
location including filename of the config file, plus the new log path to save
new results to. Note that all other flags will be ignored in an attempt to make
tests truly repeatable. If necessary, the JSON file can be manually edited to
update parameters that must change, such as hostnames.

```bash
bobber run-all --config-path /home/user/old_logs/command_parameters.json /home/user/new_logs/ test-machine-1,test-machine-2
```

## Parsing results
This repository includes a Python package that can quickly and easily parse
results captured by Bobber tests. To parse results, point the Bobber parser at
the results directory and optionally specify a filename for JSON data to be
saved to. For more information, refer to the
[parsing document](docs/parsing.md).

# Design Rationale

## Submodules

### storage-perf-test
These tests include several useful scripts that leverage fio and mdtest. Fio is
used to exercise the bandwidth and IOPS capabilities of the underlying
filesystem. Mdtest is used to exercise the metadata capabilities of the
underlying filesystem.

More about fio: https://fio.readthedocs.io/en/latest/fio_doc.html  
More about mdtest: https://github.com/hpc/ior/blob/master/doc/mdtest.1

### io-500-dev
The IO 500 repository is a convenient way to build mdtest for inclusion with
Bobber.

### nccl-tests
NCCL, or NVIDIA Collective Communications Library, is the set of primitives by
which NVIDIA GPUs communicate within systems and between systems. The nccl-tests
repository contains tests that can exercise this library, and determine latency
and bandwidth capabilities across a system or a cluster of systems.

More about nccl-tests: https://github.com/NVIDIA/nccl-tests  

### DALI
The NVIDIA DALI repository is brought along for the ResNet50 pipeline
implementation contained within the repository, and its ability to generate 
index files from TFRecords (more on that later). The DALI ResNet50 pipeline is a
good proxy test for how quickly GPUs can ingest data from an underlying
filesystem. This is a useful reference for parts of a training workload, or for
offline inference.

### Imageinary
Imageinary is a public NVIDIA repository designed to quickly create images of
JPEG, PNG, BMP, TFRecord, and RecordIO formats to feed into the DALI ResNet50
pipeline. Our rationale is that for tests that aren't intended to exercise a
neural network, the only relevant aspect of the data used to feed into the test
is its shape and format. Imageinary gives us the flexibility to avoid using
datasets such as Coco or ImageNet, and instead focus on generating a variety of
data sizes. In the future, Imageinary can be used to generate Terabyte-scale
datasets on the fly to exercise filesystems. For now, we focus on using it to
generate a consistent set of data at 800x600 and 4K resolutions to provide users
with data about how shared filesystems perform across those different sizes
and when using formats like TFRecords to aggregate data.

## Tests

### NCCL all_reduce_perf
This test measures bandwidth between GPUs within a system and across the
network. Bottlenecks within a system should be based on NVLink. Bottlenecks 
between systems should be based on the aggregate bandwidth available across the
compute network (generally 8 IB HCAs).

### Storage bandwidth
This test uses fio to measure the bandwidth performance of systems connected to
a shared filesystem. Ideally, bottlenecks would be based on the network
bandwidth available between the systems and the storage, but many systems are
likely to be unable to satisfy the maximum bandwidth capability of 4 or more DGX
systems.

### Storage IOPS
This test uses fio to measure the IO Operations Per Second capability of a
shared filesystem. This measures bandwidth to some degree, but also tests the
underlying filesystem's basic operations scalabilty due to using smaller IO
sizes (4K IOs rather than multiple MB IOs).

### Storage Metadata
This test uses mdtest to measure the performance of various metadata operations
for a shared filesystem.

### DALI ResNet50 Pipeline
This test exercises the ability of GPUs within a system to ingest data from a
shared filesystem. Imageinary is used to create files of small and large 
resolutions, and then TFRecords for each resolution. All four resulting data
formats (raw images of two sizes, TFRecords of two sizes) are ingested into all
GPUs on all systems under test. The results can then be aggregated to provide 
both an images per second result as well as a bandwidth result. 

# TODO (no particular order)
1. Get MIG testing working for DALI
2. Better self-cleanup
3. Support network tests
