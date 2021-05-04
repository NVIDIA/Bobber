# SPDX-License-Identifier: MIT
FROM nvcr.io/nvidia/tensorflow:20.11-tf2-py3

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get -y install apt-utils && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y --allow-downgrades --allow-change-held-packages --no-install-recommends \
	openssh-client \
	openssh-server \
	swig \
	bison \
	libgfortran3 \
	pkg-config \
	autotools-dev \
	debhelper \
	automake \
	m4 \
	gfortran \
	tk \
	flex \
	libltdl-dev \
	autoconf \
	dpatch \
	graphviz \
	tcl \
	chrpath \
	libglib2.0-0 \
	python-libxml2 \
	build-essential \
	cmake \
	git \
	curl \
	wget \
	ca-certificates \
	iputils-ping \
	net-tools \
	ethtool \
	perl \
	lsb-release \
	iproute2 \
	pciutils \
	kmod \
	libnuma1 \
	lsof \
	fio \
	psmisc \
	python3-distutils && \
	rm -rf /var/lib/apt/lists/*

# Set default NCCL parameters
RUN echo NCCL_DEBUG=INFO >> /etc/nccl.conf

# Install OpenSSH for MPI to communicate between containers
RUN mkdir -p /var/run/sshd && \
    mkdir -p /root/.ssh && \
    echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config && \
    echo "UserKnownHostsFile /dev/null" >> /etc/ssh/ssh_config && \
    sed -i 's/^#*Port 22/Port 2222/' /etc/ssh/sshd_config && \
    echo "HOST *" >> /root/.ssh/config && \
    echo "PORT 2222" >> /root/.ssh/config && \
    ssh-keygen -t rsa -b 4096 -f /root/.ssh/id_rsa -N "" && \
    cp /root/.ssh/id_rsa.pub /root/.ssh/authorized_keys && \
    chmod 700 /root/.ssh && \
    chmod 600 /root/.ssh/*

WORKDIR /

RUN git clone https://github.com/NVIDIA/nccl-tests && \
	cd nccl-tests/ && \
	git reset --hard ec1b5e22e618d342698fda659efdd5918da6bd9f && \
	make MPI=1 MPI_HOME=/usr/local/mpi

RUN wget --no-check-certificate https://mvapich.cse.ohio-state.edu/download/mvapich/osu-micro-benchmarks-5.6.2.tar.gz && \
	tar zxf osu-micro-benchmarks-5.6.2.tar.gz && \
	cd osu-micro-benchmarks-5.6.2 && \
	./configure CC=/usr/local/mpi/bin/mpicc CXX=/usr/local/mpi/bin/mpicxx --enable-cuda --with-cuda-include=/usr/local/cuda/include --with-cuda-libpath=/usr/local/cuda/lib64 && \
	make && \
	make install && \
	rm -rf ../*.tar.gz

RUN python3 -m pip install nvidia-pyindex && \
    python3 -m pip install \
        nvidia-imageinary['mxnet']>=1.1.2

RUN git clone https://github.com/jyvet/io-500-dev && \
	cd io-500-dev && \
	git reset --hard 0232acfa8e64f7c543db8930dd279009ec9c32bc && \
	utilities/prepare.sh

RUN git clone https://github.com/NVIDIA/DALI dali && \
	cd dali/ && \
	git reset --hard fd30786d773d08185d78988b2903dce2ace0a00b

COPY test_scripts /tests/

EXPOSE 2222
