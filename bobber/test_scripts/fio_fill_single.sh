#!/bin/bash
# SPDX-License-Identifier: MIT

cd /storage-perf-test

if [ "x$THREADS" = "x" ]; then
	THREADS=80
fi

if [ "x$DIRECTIO" = "x" ]; then
	DIRECTIO=0
fi

NO_FIO_SERVER=1 DIRECTIO=$DIRECTIO FSDIR=/mnt/fs_under_test NJOBS=$THREADS ./run_disk_fill_test.sh
