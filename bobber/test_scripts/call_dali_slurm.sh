#!/bin/bash
# SPDX-License-Identifier: MIT
if [ "x$GPUS" = "x" ]; then
	GPUS=8
fi

if [ "x$BATCH_SIZE_SM" = "x" ]; then
	BATCH_SIZE_SM=150
fi

if [ "x$BATCH_SIZE_LG" = "x" ]; then
	BATCH_SIZE_LG=150
fi

if [[ "$DATASET" == *tfrecord* ]]; then
  python3 /dali/dali/test/python/test_RN50_data_pipeline.py -b $BATCH_SIZE --epochs=11 -g $GPUS --remove_default_pipeline_paths --tfrecord_pipeline_paths "$DATASET"
else
  python3 /dali/dali/test/python/test_RN50_data_pipeline.py -b $BATCH_SIZE --epochs=11 -g $GPUS --remove_default_pipeline_paths --file_read_pipeline_paths "$DATASET"
fi
