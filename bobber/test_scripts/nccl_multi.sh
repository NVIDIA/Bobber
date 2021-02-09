#!/bin/bash
# SPDX-License-Identifier: MIT

if [ "x$GPUS" = "x" ]; then
	GPUS=8
fi

if [ "x$HOSTS" = "x" ]; then
	HOSTS=localhost:$GPUS
fi

if [ "x$NCCL_IB_HCAS" = "x" ]; then
	NCCL_IB_HCAS=mlx5_0,mlx5_1,mlx5_2,mlx5_3,mlx5_6,mlx5_7,mlx5_8,mlx5_9
fi

if [ "x$SSH_IFACE" = "x" ]; then
	SSH_IFACE=enp226s0
fi

if [ "x$NCCL_MAX" = "x" ]; then
	NCCL_MAX=1
fi

if [ "x$COMPUTE_GID" = "x" ]; then
	COMPUTE_GID=0
fi

if [ "x$NCCL_TC" = "x" ]; then
	NCCL_TC=''
fi

IFS="," read -r -a HOST_ARRAY <<< "$HOSTS"

HOST_COUNT=${#HOST_ARRAY[@]}

#remove trailing comma when passing the argument
for i in ${HOST_ARRAY[@]}; do
	HOST_STRING+="$i:$GPUS,"
done

mpirun -report-uri -display-allocation -v --allow-run-as-root --np $(($GPUS*$HOST_COUNT)) -H ${HOST_STRING%?} -bind-to none -map-by slot -x IBV_DRIVERS -x LD_LIBRARY_PATH -x PATH -x NCCL_IB_HCA=$NCCL_IB_HCAS -x NCCL_IB_TC=$NCCL_TC -x NCCL_IB_GID_INDEX=$COMPUTE_GID -x NCCL_IB_CUDA_SUPPORT=1 -mca orte_base_help_aggregate 0 -mca plm_rsh_agent ssh -mca plm_rsh_args "-p 2222" -mca pml ob1 -mca btl ^openib -mca btl_tcp_if_include $SSH_IFACE -mca btl_openib_verbose 1 /nccl-tests/build/all_reduce_perf -b 8 -e ${NCCL_MAX}G -f 2
