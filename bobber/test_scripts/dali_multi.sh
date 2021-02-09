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

GPUS_ZERO_BASE=$(($GPUS-1))

if [ "x$HOSTS" = "x" ]; then
	HOSTS=localhost:1
fi

if [ "x$SSH_IFACE" = "x" ]; then
	SSH_IFACE=enp226s0
fi

IFS=',' read -r -a HOST_ARRAY <<< "$HOSTS"

HOST_COUNT=${#HOST_ARRAY[@]}

#remove trailing comma when passing the argument
for i in ${HOST_ARRAY[@]}; do
	HOST_STRING+="$i:$GPUS,"
done

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

mpirun --allow-run-as-root -H ${HOST_STRING%?} -bind-to none -map-by ppr:1:node --mca plm_rsh_agent ssh -mca plm_rsh_args "-p 2222" -mca btl_tcp_if_include $SSH_IFACE /tests/call_dali_multi.sh $BATCH_SIZE_SM /mnt/fs_under_test/imageinary_data/800x600/file_read_pipeline_images $GPUS
mpirun --allow-run-as-root -H ${HOST_STRING%?} -bind-to none -map-by ppr:1:node --mca plm_rsh_agent ssh -mca plm_rsh_args "-p 2222" -mca btl_tcp_if_include $SSH_IFACE sysctl vm.drop_caches=3

mpirun --allow-run-as-root -H ${HOST_STRING%?} -bind-to none -map-by ppr:1:node --mca plm_rsh_agent ssh -mca plm_rsh_args "-p 2222" -mca btl_tcp_if_include $SSH_IFACE /tests/call_dali_multi.sh $BATCH_SIZE_LG /mnt/fs_under_test/imageinary_data/3840x2160/file_read_pipeline_images $GPUS
mpirun --allow-run-as-root -H ${HOST_STRING%?} -bind-to none -map-by ppr:1:node --mca plm_rsh_agent ssh -mca plm_rsh_args "-p 2222" -mca btl_tcp_if_include $SSH_IFACE sysctl vm.drop_caches=3

mpirun --allow-run-as-root -H ${HOST_STRING%?} -bind-to none -map-by ppr:1:node --mca plm_rsh_agent ssh -mca plm_rsh_args "-p 2222" -mca btl_tcp_if_include $SSH_IFACE /tests/call_dali_multi.sh $BATCH_SIZE_SM "/mnt/fs_under_test/imageinary_data/800x600/tfrecord_pipeline/tfrecord-*" $GPUS
mpirun --allow-run-as-root -H ${HOST_STRING%?} -bind-to none -map-by ppr:1:node --mca plm_rsh_agent ssh -mca plm_rsh_args "-p 2222" -mca btl_tcp_if_include $SSH_IFACE sysctl vm.drop_caches=3

mpirun --allow-run-as-root -H ${HOST_STRING%?} -bind-to none -map-by ppr:1:node --mca plm_rsh_agent ssh -mca plm_rsh_args "-p 2222" -mca btl_tcp_if_include $SSH_IFACE /tests/call_dali_multi.sh $BATCH_SIZE_LG "/mnt/fs_under_test/imageinary_data/3840x2160/tfrecord_pipeline/tfrecord-*" $GPUS
mpirun --allow-run-as-root -H ${HOST_STRING%?} -bind-to none -map-by ppr:1:node --mca plm_rsh_agent ssh -mca plm_rsh_args "-p 2222" -mca btl_tcp_if_include $SSH_IFACE sysctl vm.drop_caches=3

rm -r /mnt/fs_under_test/imageinary_data
