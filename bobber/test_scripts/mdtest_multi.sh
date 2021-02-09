#!/bin/bash
# SPDX-License-Identifier: MIT

#force threads to 44 for now - unclear on why we can't use more threads with mdtest but it blows up
THREADS=44
FSDIR=/mnt/fs_under_test

mkdir $FSDIR/mdtest

if [ "x$HOSTS" = "x" ]; then
	HOSTS=localhost:$THREADS
fi

if [ "x$NCCL_IB_HCAS" = "x" ]; then
	NCCL_IB_HCAS=mlx5_0,mlx5_1,mlx5_2,mlx5_3,mlx5_6,mlx5_7,mlx5_8,mlx5_9
fi

if [ "x$SSH_IFACE" = "x" ]; then
	SSH_IFACE=enp226s0
fi

IFS="," read -r -a HOST_ARRAY <<< "$HOSTS"

HOST_COUNT=${#HOST_ARRAY[@]}

#remove trailing comma when passing the argument
HOST_STRING=""
for i in ${HOST_ARRAY[@]}; do
	HOST_STRING+="$i:$THREADS,"
done

set -x

mpirun -np $(($HOST_COUNT*$THREADS)) -H ${HOST_STRING%?} -map-by ppr:$THREADS:node --allow-run-as-root --mca btl_openib_warn_default_gid_prefix 0 --mca btl_openib_if_exclude mlx5_0,mlx5_5,mlx5_6 --mca plm_base_verbose 0 --mca plm_rsh_agent ssh -x IBV_DRIVERS -mca btl_tcp_if_include $SSH_IFACE -mca plm_rsh_args "-p 2222" /io-500-dev/bin/mdtest -i 3 -I 4 -z 3 -b 8 -u -d $FSDIR/mdtest

rm -rf $FSDIR/mdtest
