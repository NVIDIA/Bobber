#!/bin/bash
# SPDX-License-Identifier: MIT
BATCH_SIZE=$1
DATASET=$2
GPUS=$3

if [[ "$DATASET" == *tfrecord* ]]; then
  python3 /dali/dali/test/python/test_RN50_data_pipeline.py -b $BATCH_SIZE --epochs=11 -g $GPUS --remove_default_pipeline_paths --tfrecord_pipeline_paths "$DATASET"
else
  python3 /dali/dali/test/python/test_RN50_data_pipeline.py -b $BATCH_SIZE --epochs=11 -g $GPUS --remove_default_pipeline_paths --file_read_pipeline_paths "$DATASET"
fi
