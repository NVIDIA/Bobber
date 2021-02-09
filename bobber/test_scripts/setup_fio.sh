drop_caches () {

	DC=0
        case $FSTYPE in
            gpfs)
                echo "Cannot drop cache on GPFS"
                ;;
            lustre|nfs|ext4|wekafs)
                DC=1
                ;;
            *)
                echo "Unable to determine how to drop cache on FSTYPE: $FSTYPE, dropping anyway"
                DC=1
                ;;
        esac
	if [ $DC -eq 1 ]; then
		echo "Starting Drop Caches: $(date)"
		declare -a pidlist
		unset pidlist
		for N in ${FIO_NODELIST}; do
            ssh $N $SSHOPTS /sbin/sysctl vm.drop_caches=3 &
		    p=$!
		    pidlist=(${pidlist[@]} $p)
        done
		wait ${pidlist[@]}
		echo "Ending Drop Caches: $(date)"
	fi
}

stop_servers () {

    declare -a pidlist
    pidlist=""
    for N in $FIO_NODELIST; do
        echo "Killing Server on $N"

	    if [ "$N" == "localhost" ]; then
	        killall fio
        else
            ssh ${SSHOPTS} $N killall fio > /dev/null 2>&1 &
	    fi
        p=$!
        pidlist=(${pidlist[@]} $p)
    done
    wait ${pidlist[@]}
}

start_servers () {

    if [ x"$NO_FIO_SERVER" != x"1" ]; then
        declare -a pidlist
        pidlist=""
        for N in $FIO_NODELIST; do
            echo "Launching Server on $N"

        	if [ "$N" == "localhost" ]; then
    	        $FIOBIN --server --daemonize=/tmp/pidfile.$$ > /dev/null 2>&1 &
            else
                ssh ${SSHOPTS} $N $FIOBIN --server --daemonize=/tmp/pidfile.$$ > /dev/null 2>&1 &
        	fi
            p=$!
            pidlist=(${pidlist[@]} $p)
        done
        wait ${pidlist[@]}
    else
       echo "Not Starting FIO Server"
    fi
}

create_jobfile () {

    # Write job to stdout
    echo "[${NAME}]"
    for O in $@; do
	if [ "$O" != "--create_jobfile" ]; then
		echo $O | sed 's/^\-\-//g'
	fi
    done
}

launch_fio () {

    echo "Command: "
    echo $FIOBIN $@

    # Create Job File
    JOBFN=.jobfn.$$
    create_jobfile $@ > $JOBFN
    cat $JOBFN

    if [ x"$NO_FIO_SERVER" != x"1" ]; then

        # Run Jobfile
        MFILE=/tmp/mfile.$$
        rm -f $MFILE
        echo $FIO_NODELIST | tr ' ' '\n' > $MFILE

        $FIOBIN --client=$MFILE $JOBFN

        # Cleanup job file
        rm -rf $JOBFN
        rm -f $MFILE
    else
	    taskset -c 0-23,48-71 $FIOBIN $JOBFN
    fi
}

#Filesystem type
export FSTYPE=$(df -T $FSDIR | tail -1 | awk '{print $2}')
# Set Size of file per thread
export SIZE=${SIZE:-$(( 4096 * 1024 ))}
# Set Size of each IO in KB
export IOSIZE=${IOSIZE:-1024}
# Set size of the IOs for file creation in KB
export CREATE_IOSIZE=${CREATE_IOSIZE:-1024}
# Number of Files per job
export NRFILES=${NRFILES:-256}
# Use DirectIO?
export DIRECTIO=${DIRECTIO:-0}
# Use MMAP IO?
export MMAPIO=${MMAPIO:-0}
# Set IODepth for DirectIO cases
export IODEPTH=${IODEPTH:-16}
# Set the invalidate flag or not, default is yes
export INVALIDATE=${INVALIDATE:-1}
# Set SSH options
export SSHOPTS=${SSHOPTS:-"-o StrictHostKeyChecking=no"}
# Set extra flags, if present
export EXTRA_FLAGS=${EXTRA_FLAGS:-""}
# Set JobName
export NAME=${NAME:-iotest}
# Set DirectIO settings if needed, allow for IOENGINE flexibility
export IOENGINE=${IOENGINE:-posixaio}
IOSETTINGS=""

if [ $DIRECTIO -eq 1 ] && [ $MMAPIO -eq 1 ]; then
	echo "ERROR, unable to use both Direct IO and MMAP I/O simultaenously.  Exiting"
	exit 1
fi

if [ $DIRECTIO -eq 1 ]; then
   IOSETTINGS="--direct=${DIRECTIO} --ioengine=${IOENGINE} --iodepth=${IODEPTH}"
fi

if [ $MMAPIO -eq 1 ]; then
   IOSETTINGS="--ioengine=mmap"
fi

# Set FSYNC if needed
if [ x"$FSYNC" != x"" ]; then
        FSYNC="--fsync=${FSYNC}"
fi

#### Settings to run
FIOBIN=${FIOBIN:-fio}

if [ x"$(which $FIOBIN)" == x"" ]; then
	echo "ERROR: Enable to find fio binary at <$FIOBIN>.  Set with FIOBIN. Exiting"
	exit
fi

FIODIR=$(cd $(dirname $(which $FIOBIN)) && pwd)
FIOBIN=$FIODIR/$(basename $FIOBIN)

DATETAG=$(date +%Y%m%d%H%M%S)

export STDOPTS="--create_serialize=0 --fallocate=none --group_reporting=1 --disable_lat=1 --disable_clat=1 --disable_slat=1 --startdelay=5 --ramp_time=3 --runtime=180 --time_based=1"

echo "IOTEST Settings:"
for E in FSDIR FSTYPE NJOBS SIZE IOSIZE NRFILES DIRECTIO MMAPIO IOSETTINGS INVALIDATE FSYNC STDOPTS FIOBIN DATETAG SSHOPTS RUNTIME EXTRA_FLAGS; do
        eval V=\$$E
        echo $E | awk '{printf("%-12s: ", $1);}'
        echo $V
done
echo ""

########## Create
WORKDIR=$FSDIR/fiodir.$DATETAG
echo "Creating output directory $WORKDIR"
mkdir $WORKDIR

########## Use nodelist from Bobber
FIO_NODELIST=$HOSTS_WITH_SPACES
echo "NCOUNT : $(echo $FIO_NODELIST | wc -w)"

if [ x"$(which numactl)" != x"" ]; then
    numactl --show
fi

echo "FIO_NODELIST: $FIO_NODELIST"
