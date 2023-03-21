#!/bin/bash
#SBATCH --job-name bobber_mdtest
# SPDX-License-Identifier: MIT
set -euxo pipefail

FSDIR=/mnt/fs_under_test
mkdir -p $FSDIR/mdtest

# N-hosts * 44 (default thread count) processes
/io-500-dev/bin/mdtest -i 3 -I 4 -z 3 -b 8 -u -d $FSDIR/mdtest

rm -rf $FSDIR/mdtest
