#!/bin/bash
# SPDX-License-Identifier: MIT

if [ "x$NCCL_IB_HCAS" = "x" ]; then
	NCCL_IB_HCAS=mlx5_0,mlx5_1,mlx5_2,mlx5_3,mlx5_6,mlx5_7,mlx5_8,mlx5_9
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

export NCCL_IB_HCA=$NCCL_IB_HCAS && \
  export NCCL_IB_TC=$NCCL_TC && \
  export NCCL_IB_GID_INDEX=$COMPUTE_GID && \
  export NCCL_IB_CUDA_SUPPORT=1 && \
  /nccl-tests/build/all_reduce_perf -b 8 -e ${NCCL_MAX}G -f 2
