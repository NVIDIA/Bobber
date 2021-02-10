# Docker
This document demonstrates how to verify Docker installations and proper GPU
functionality for Docker containers.

## Docker installation/upgrade
This project requires Docker version 19.03 or newer to be installed. Check the
version of Docker installed on the system with

```bash
docker --version
```

If the version is 19.03 or newer, you may continue to the next sub-section.

If your Docker version is older than 19.03, or Docker is not installed, follow
the steps listed on Docker's website for
[upgrading the Docker client](https://docs.docker.com/engine/install/ubuntu/),
which are copied below for reference:

First, remove any existing installations:

```bash
sudo apt-get remove docker docker-engine docker.io containerd runc
```

Next, install required dependencies and add the Docker GPG key:

```bash
sudo apt-get update

sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
```

Lastly, add the stable repository and install Docker:

```bash
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io
```

## Docker permissions
By default, only the `root` user is able to use Docker. To enable other users to
use Docker without `sudo`, the user must be added to the `docker` group:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

Verify your user is now able to interact directly with Docker without `sudo`:

```bash
$ docker images
REPOSITORY                         TAG                     IMAGE ID            CREATED             SIZE
```

## Install NVIDIA-Docker
In order to access GPUs inside Docker containers, the `nvidia-docker` package
needs to be installed on all systems. The following installs the package
(taken from [the nvidia-docker docs](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker)):

```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) && \
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - && \
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt update
sudo apt install nvidia-docker2
sudo systemctl restart docker
```

## Testing containers
Once Docker is fully installed, ensure GPUs are accessible from containers by
pulling a CUDA container and running `nvidia-smi`:

```bash
docker run --rm -it --gpus all nvidia/cuda:11.0-base nvidia-smi
```

This should output information on the GPUs installed on a system, similar to
below:

```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 450.51.06    Driver Version: 450.51.06    CUDA Version: 11.0     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                               |                      |               MIG M. |
|===============================+======================+======================|
|   0  A100-SXM4-40GB      On   | 00000000:07:00.0 Off |                    0 |
| N/A   31C    P0    62W / 400W |      0MiB / 40537MiB |      0%      Default |
|                               |                      |             Disabled |
+-------------------------------+----------------------+----------------------+
|   1  A100-SXM4-40GB      On   | 00000000:0F:00.0 Off |                    0 |
| N/A   29C    P0    60W / 400W |      0MiB / 40537MiB |      0%      Default |
|                               |                      |             Disabled |
+-------------------------------+----------------------+----------------------+
|   2  A100-SXM4-40GB      On   | 00000000:47:00.0 Off |                    0 |
| N/A   30C    P0    63W / 400W |      0MiB / 40537MiB |      0%      Default |
|                               |                      |             Disabled |
+-------------------------------+----------------------+----------------------+
|   3  A100-SXM4-40GB      On   | 00000000:4E:00.0 Off |                    0 |
| N/A   30C    P0    60W / 400W |      0MiB / 40537MiB |      0%      Default |
|                               |                      |             Disabled |
+-------------------------------+----------------------+----------------------+
|   4  A100-SXM4-40GB      On   | 00000000:87:00.0 Off |                    0 |
| N/A   34C    P0    64W / 400W |      0MiB / 40537MiB |      0%      Default |
|                               |                      |             Disabled |
+-------------------------------+----------------------+----------------------+
|   5  A100-SXM4-40GB      On   | 00000000:90:00.0 Off |                    0 |
| N/A   33C    P0    66W / 400W |      0MiB / 40537MiB |      0%      Default |
|                               |                      |             Disabled |
+-------------------------------+----------------------+----------------------+
|   6  A100-SXM4-40GB      On   | 00000000:B7:00.0 Off |                    0 |
| N/A   34C    P0    61W / 400W |      0MiB / 40537MiB |      0%      Default |
|                               |                      |             Disabled |
+-------------------------------+----------------------+----------------------+
|   7  A100-SXM4-40GB      On   | 00000000:BD:00.0 Off |                    0 |
| N/A   33C    P0    58W / 400W |      0MiB / 40537MiB |      0%      Default |
|                               |                      |             Disabled |
+-------------------------------+----------------------+----------------------+
                                                                               
+-----------------------------------------------------------------------------+
| Processes:                                                                  |
|  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
|        ID   ID                                                   Usage      |
|=============================================================================|
|  No running processes found                                                 |
+-----------------------------------------------------------------------------+
```