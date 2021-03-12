# Non-DGX Support
While Bobber supports both the NVIDIA DGX A100 and the DGX-2 platforms out of
the box, it can also be run on most non-DGX Linux-based platforms with at least
one NVIDIA Turing-based architecture or newer GPU installed. Depending on the
systems being tested, a few parameters will need to be updated for Bobber to run
as intended. This guide provides information on how to find the parameters to
use:

## GPU Count
By default, Bobber expects 8 GPUs in a system, similar to the DGX A100. If a
system has a different number of GPUs installed than the default value, it will
need to be specified by passing the `--gpus N` flag to any of the test Bobber
test commands. To find the number of NVIDIA GPUs available, use `nvidia-smi` to
list system-level GPU information. The following will list the GPUs installed on
a system:

```bash
$ nvidia-smi --query-gpu=gpu_name --format=csv,noheader
Quadro RTX 8000
Quadro RTX 8000
```

In the example above, the system has two RTX 8000 GPUs available. To run a test
with this system, the `--gpus 2` flag will need to be passed, similar to the
following:

```bash
$ bobber run-all --gpus 2 /home/user/logs test-machine-1
```

At present, Bobber assumes all test systems in a cluster have the **same**
number of GPUs available. To run a test pass with multiple nodes that all have
two GPUs, run the following:

```bash
$ bobber run-all --gpus 2 /home/user/logs test-machine-1,test-machine-2,...
```

## SSH Interface
While not important for single-node tests, the `--ssh-iface` flag is used to
tell Bobber which network interface to use to communicate with other test nodes
for multi-node tests. This can be found by using the `ip link show` command to
list the active network interfaces on a system:

```bash
$ ip link show | grep "state UP"
2: enp67s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP mode DEFAULT group default qlen 1000
4: wlo2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DORMANT group default qlen 1000
```

The example above shows two interfaces are "UP" - `enp67s0` which is a wired
connection and `wlo2` which is a wireless connection. For this system, the wired
connection is desired as it should provide better stability and performance. In
general, the chosen interface should also be the primary management interface
used by the operating system.

To use `enp67s0` as the interface per the example above, tests can be started
with:

```bash
bobber run-all --ssh-iface enp67s0 /home/user/logs test-machine-1,test-machine-2,...
```

## DALI Batch Sizes
The DALI preprocesses large and small images which is typical of ResNet50
workflows. Depending on the amount of GPU memory available, the DALI tests could
run out of memory and terminate prematurely. Lowering the batch size for DALI
allows the GPUs to allocate less memory to the test, enabling the process to
complete as intended. It is recommended to attempt the tests once with the
default batch sizes to verify successful completion. If the GPUs ran out of
memory, a line similar to the following will be shown in the test log (note
that the line number (`11`) and process number (`5349`) may differ):

```
/tests/call_dali_multi.sh: line 11:  5349 Killed
```

This will also be accompanied by the following mpirun error:

```
--------------------------------------------------------------------------
Primary job  terminated normally, but 1 process returned
a non-zero exit code. Per user-direction, the job has been aborted.
--------------------------------------------------------------------------
--------------------------------------------------------------------------
mpirun detected that one or more processes exited with non-zero status, thus causing
the job to be terminated. The first process to do so was:
  Process name: [[37996,1],0]
  Exit code:    137
--------------------------------------------------------------------------
```

If this error is shown, drop the batch size by half and restart the test to see
if it completes successfully. Continue this process until the test is able to
run. While it is possible both the small and large image sizes are causing the
GPUs to run out of memory, it is much more likely that the large image batch
size needs to be dropped. The default batch size for large images is `256` and
for small images it is `512`. Specify the batch sizes with the following:

```bash
$ bobber run-dali --batch-size-lg 128 --batch-size-sm 256 /home/user/logs test-machine-1,test-machine-2,...
# OR
$ bobber run-all --batch-size-lg 128 --batch-size-sm 256 /home/user/logs test-machine-1,test-machine-2,...
```

## FIO Thread Flags
Depending on the performance of the filesystem under test in addition to the
CPUs, the FIO tests might stall, though this is very unlikely. If any of the FIO
tests are stuck for a long time (10 minutes or more), the thread counts for both
IOPS and bandwidth tests can be dropped to a lower level. These can be specified
with the `--iops-threads` and `--bw-threads` flags. Note that for high
performance filesystems and beefy compute nodes, these values can also be
increased to attempt to achieve higher test results. The flags can be specified
as follows:

```bash
$ bobber run-all --iops-threads 100 --bw-threads 32 /home/user/logs test-machine-1,test-machine-2,...
```

## NCCL HCAs
The NCCL tests use specific HCAs to communicate across nodes. At present, this
requires NVIDIA Mellanox network adapters connected between nodes either
directly or via a network switch. For most server configurations, there will be
a dedicated compute fabric used for high-speed communication between nodes.
These adapters should be targeted for the NCCL tests. To find the appropriate
adapters, run `ibdev2netdev` to find the HCA device name that corresponds to the
network device name for the compute network. For example, consider the following
output:

```bash
$ ibdev2netdev
mlx5_0 ==> ib0 (Up)
mlx5_1 ==> ib1 (Up)
mlx5_10 ==> ib10 (Up)
mlx5_11 ==> ib11 (Up)
mlx5_2 ==> ib2 (Up)
mlx5_3 ==> ib3 (Up)
mlx5_4 ==> ib4 (Up)
mlx5_5 ==> ib5 (Up)
mlx5_6 ==> ib6 (Up)
mlx5_7 ==> ib7 (Up)
mlx5_8 ==> ib8 (Up)
mlx5_9 ==> ib9 (Up)
```

If the compute network is on adapters ib0-ib7, the devices to use for NCCL are
`mlx5_0`, `mlx5_1`, ..., `mlx5_7`, matching the list above. To use these devices
for the NCCL tests, the `--nccl-ib-hcas` flag needs to be passed, similar to the
following. Note that the devices are separated with commas and no spaces:

```bash
$ bobber run-all --nccl-ib-hcas mlx5_0,mlx5_1,mlx5_2,mlx5_3,mlx5_4,mlx5_5,mlx5_6,mlx5_7 /home/user/logs test-machine-1,test-machine-2,...
# OR
$ bobber run-nccl --nccl-ib-hcas mlx5_0,mlx5_1,mlx5_2,mlx5_3,mlx5_4,mlx5_5,mlx5_6,mlx5_7 /home/user/logs test-machine-1,test-machine-2,...
```
