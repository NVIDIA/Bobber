# SPDX-License-Identifier: MIT
# Larger base stage with required items for building various tools
FROM nvcr.io/nvidia/cuda:11.2.0-devel-ubuntu20.04 as build

ENV DEBIAN_FRONTEND=noninteractive

# Install all required build dependencies
RUN apt-get update && apt-get -y install apt-utils && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y --allow-downgrades --allow-change-held-packages --no-install-recommends \
	swig \
	bison \
	gcc \
	libgfortran4 \
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
	libopenmpi-dev && \
	rm -rf /var/lib/apt/lists/*

# Compile NVIDIA's NCCL tests
RUN git clone https://github.com/NVIDIA/nccl-tests && \
	cd nccl-tests/ && \
	git reset --hard ec1b5e22e618d342698fda659efdd5918da6bd9f && \
	make MPI=1 MPI_HOME=/usr/lib/x86_64-linux-gnu/openmpi

# Compile OSU microbenchmarks
RUN wget --no-check-certificate https://mvapich.cse.ohio-state.edu/download/mvapich/osu-micro-benchmarks-5.6.2.tar.gz && \
	tar zxf osu-micro-benchmarks-5.6.2.tar.gz && \
	cd osu-micro-benchmarks-5.6.2 && \
	./configure CC=/usr/bin/mpicc CXX=/usr/bin/mpicxx --enable-cuda --with-cuda-include=/usr/local/cuda/include --with-cuda-libpath=/usr/local/cuda/lib64 && \
	make && \
	make install && \
	rm -rf ../*.tar.gz

# Build IO500, IOR, and mdtest
RUN git clone https://github.com/jyvet/io-500-dev && \
	cd io-500-dev && \
	git reset --hard 0232acfa8e64f7c543db8930dd279009ec9c32bc && \
	utilities/prepare.sh

# Lighter runtime stage copying only necessary build artifacts from earlier
FROM nvcr.io/nvidia/cuda:11.2.0-runtime-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --allow-downgrades --allow-change-held-packages --no-install-recommends \
	openssh-client \
	openssh-server \
	git \
	fio \
	psmisc \
	libopenmpi-dev \
	openmpi-bin \
	python \
	python3-dev \
	python3-pip \
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

# Copy the compiled nccl-tests binaries to the runtime image
COPY --from=build /nccl-tests/build /nccl-tests/build

# Copy the compiled OSU microbenchmarks to the runtime image
COPY --from=build /usr/local/libexec/osu-micro-benchmarks/mpi/collective/ /usr/local/libexec/osu-micro-benchmarks/mpi/collective/

# Copy the compiled IO500 binaries to the runtime image
COPY --from=build /io-500-dev/bin /io-500-dev/bin

RUN git clone https://github.com/NVIDIA/DALI dali && \
	cd dali/ && \
	git reset --hard fd30786d773d08185d78988b2903dce2ace0a00b

RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools && \
    python3 -m pip install --no-cache-dir nvidia-pyindex && \
    python3 -m pip install --no-cache-dir \
        nvidia-imageinary['tfrecord']>=1.1.2 \
        nvidia-dali-cuda110

COPY test_scripts /tests/

EXPOSE 2222
