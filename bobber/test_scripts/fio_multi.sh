#!/bin/bash

if [ "x$THREADS" = "x" ]; then
	THREADS=80
fi

if [ "x$DIRECTIO" = "x" ]; then
        DIRECTIO=0
fi

if [ "x$HOSTS" = "x" ]; then
	HOSTS=''
fi

if [ "x$IO_DEPTH" = "x" ]; then
        IO_DEPTH=16
fi

if [ "x$EXTRA_FLAGS" = "x" ]; then
        EXTRA_FLAGS=''
fi

HOSTS_WITH_SPACES=`echo $HOSTS | sed "s/,/ /g"`

FSDIR=/mnt/fs_under_test

IODEPTH=$IO_DEPTH
NJOBS=$THREADS

# Process all settings
source /tests/setup_fio.sh

# Clean up old jobs
stop_servers

# Start servers
start_servers

RUNOPTS="--invalidate=${INVALIDATE} --blocksize=${IOSIZE}k --size=${SIZE}k --numjobs=${NJOBS} --directory=${WORKDIR} ${FSYNC}"
CREATEOPTS="--invalidate=${INVALIDATE} --blocksize=${CREATE_IOSIZE}k --size=${SIZE}k --numjobs=${NJOBS} --directory=${WORKDIR} ${FSYNC}"

# List of commands
## Run create only first as it has been said it improves performance
## Run create with a large blocksize, because using a smaller blocksize will take an inordinate amount of time
launch_fio --create_only=1 --rw=write ${IOSETTINGS} ${STDOPTS} ${CREATEOPTS}

launch_fio --rw=write ${IOSETTINGS} ${STDOPTS} ${RUNOPTS} ${EXTRA_FLAGS}
drop_caches

launch_fio --rw=read ${IOSETTINGS} ${STDOPTS} ${RUNOPTS} ${EXTRA_FLAGS}
drop_caches

# Clean up the job
stop_servers

echo "Cleaning workspace"
rm -f $JOBFN
if [ "x$NORMDATA" == "x" ]; then
        rm -rf $WORKDIR
fi

echo "Done Running FIO Test"
