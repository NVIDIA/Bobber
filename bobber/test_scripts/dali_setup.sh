#!/bin/bash
# SPDX-License-Identifier: MIT
if [ "x$GPUS" = "x" ]; then
	GPUS=8
fi

GPUS_ZERO_BASE=$(($GPUS-1))

mkdir -p /mnt/fs_under_test/imageinary_data/3840x2160/file_read_pipeline_images/images
mkdir -p /mnt/fs_under_test/imageinary_data/800x600/file_read_pipeline_images/images
mkdir -p /mnt/fs_under_test/imageinary_data/3840x2160/tfrecord_pipeline
mkdir -p /mnt/fs_under_test/imageinary_data/800x600/tfrecord_pipeline
mkdir -p /mnt/fs_under_test/imageinary_data/3840x2160/tfrecord_pipeline.idx
mkdir -p /mnt/fs_under_test/imageinary_data/800x600/tfrecord_pipeline.idx

imagine create-images --path /mnt/fs_under_test/imageinary_data/3840x2160/file_read_pipeline_images/images --name 4k_image_ --width 3840 --height 2160 --count $(($GPUS*1000)) --image_format jpg --size
imagine create-images --path /mnt/fs_under_test/imageinary_data/800x600/file_read_pipeline_images/images --name small_image_ --width 800 --height 600 --count $(($GPUS*1000)) --image_format jpg --size

imagine create-tfrecords --source_path /mnt/fs_under_test/imageinary_data/3840x2160/file_read_pipeline_images/images --dest_path /mnt/fs_under_test/imageinary_data/3840x2160/tfrecord_pipeline --name tfrecord- --img_per_file 1000
imagine create-tfrecords --source_path /mnt/fs_under_test/imageinary_data/800x600/file_read_pipeline_images/images --dest_path /mnt/fs_under_test/imageinary_data/800x600/tfrecord_pipeline --name tfrecord- --img_per_file 1000

for i in $(seq 0 $GPUS_ZERO_BASE); do /dali/tools/tfrecord2idx /mnt/fs_under_test/imageinary_data/3840x2160/tfrecord_pipeline/tfrecord-$i /mnt/fs_under_test/imageinary_data/3840x2160/tfrecord_pipeline.idx/tfrecord-$i; done
for i in $(seq 0 $GPUS_ZERO_BASE); do /dali/tools/tfrecord2idx /mnt/fs_under_test/imageinary_data/800x600/tfrecord_pipeline/tfrecord-$i /mnt/fs_under_test/imageinary_data/800x600/tfrecord_pipeline.idx/tfrecord-$i; done
