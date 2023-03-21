#!/bin/bash
# SPDX-License-Identifier: MIT

if [ "x$GPUS" = "x" ]; then
	GPUS=8
fi

if [ "x$BATCH_SIZE" = "x" ]; then
	BATCH_SIZE=150
fi

if [ "x$DATASET_PATH" = "x" ]; then
    DATASET_PATH="/mnt/fs_under_test/imageinary_data/800x600/file_read_pipeline_images"
fi

python3 /dali/dali/test/python/test_RN50_data_pipeline.py -b $BATCH_SIZE --epochs=11 -g $GPUS --remove_default_pipeline_paths --file_read_pipeline_paths /mnt/fs_under_test/imageinary_data/800x600/file_read_pipeline_images
