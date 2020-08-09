#!/bin/bash

###########################################
#
# Define VARS
#
###########################################

#SBATCH Runtime EVV Options
SPEC_ARCH="CPU"
SPEC_NPROC=1
SPEC_NODES=1
SPEC_NTPN="--ntasks-per-node=1"
SPEC_THPC="--threads-per-core=1"
SPEC_PART="--partition=allq"
SPEC_GRES=""
SPEC_EXCL="--exclusive"
SPEC_rque="--requeue"
SPEC_MPIR="echo"
MONE_NPROC="niner"

#SBATCH Job Options
WAIT_JID="NONE"
JOB_NAME="specfem3d"
OLOG="log.out"
ELOG="log.err"
PROG="echo"
PROG_ARG="NONE"
LOG_PATH="./"

#For checing that only CPU or GPU is defined
NCPU="0" 
NGPU="1"

###########################################
#
# Read arguments
#
###########################################

for i in "$@"; do
  case $i in
    -nCPU=*)
    SPEC_NPROC="${i#*=}"
    SPEC_NTPN="--ntasks-per-node=$SPEC_NPROC"
    NCPU="SET"
    ;;
    -nGPU=*)
    SPEC_NPROC="${i#*=}"
    SPEC_NODES=$SPEC_NPROC
    SPEC_ARCH="GPU"
    SPEC_PART="--partition=gpu"
    SPEC_GRES="--gres=gpu"
    NGPU="SET"
    ;;
    -lp=*)
    LOG_PATH="${i#*=}"
    ;;
    -w=*)
    WAIT_JID="-d ${i#*=}"
    ;;
    -jn=*)
    JOB_NAME="${i#*=}"
    ;;
    -o=*)
    OLOG="${i#*=}"
    ;;
    -e=*)
    ELOG="${i#*=}"
    ;;
    -x=*)
    PROG="${i#*=}"
    ;;
    -xa=*)
    PROG_ARG="${i#*=}"
    ;;
    *)
    echo "unknown option"
    exit 2;
    ;;
  esac
done

if [[ $NCPU == $NGPU ]]; then
  echo "-nCPU and -nGPU cannot both be set at the same time.";
  exit 2;
fi

MONE_NPROC=`expr $SPEC_NPROC - 1`;
SPEC_MPIR="mpirun -np $SPEC_NPROC -genv I_MPI_PIN_PROCESSOR_LIST=0-$MONE_NPROC -genv I_MPI_FABRICS=shm:ofa "

if [[ $SPEC_ARCH == GPU ]]; then
  SPEC_MPIR="mpirun -np $NPROC --mca btl_openib_cuda_rdma_limit 100000 "
fi

if [[ $WAIT_JID == "NONE" ]]; then
  WAIT_JID=""
fi

if [[ $PROG_ARG == "NONE" ]]; then
  PROG_ARG=""
fi

OLOG=${LOG_PATH}${OLOG}
ELOG=${LOG_PATH}${ELOG}

LDATE=`date +.on.%F.at.%H:%M:%S`
SBLOG="${LOG_PATH}${JOB_NAME}${LDATE}.sblog"

###########################################
#
# Run Job
#
###########################################

echo "source ../env/set_base_project_env.sh" > ${SBLOG};
source ../env/set_base_project_env.sh;

SB_ARGS="-n $SPEC_NPROC"
SB_ARGS="${SB_ARGS} -N $SPEC_NODES"
SB_ARGS="${SB_ARGS} $SPEC_NTPN"
SB_ARGS="${SB_ARGS} $SPEC_THPC"
SB_ARGS="${SB_ARGS} $SPEC_PART"
SB_ARGS="${SB_ARGS} $SPEC_GRES"
SB_ARGS="${SB_ARGS} $SPEC_EXCL"
SB_ARGS="${SB_ARGS} -o $OLOG"
SB_ARGS="${SB_ARGS} -e $ELOG"
SB_ARGS="${SB_ARGS} -J $JOB_NAME"
SB_ARGS="${SB_ARGS} $WAIT_JID"

SB_EXPORT="--export=ALL,SPEC_ARCH=$SPEC_ARCH,SPEC_NPROC=$SPEC_NPROC"
#SB_EXPORT=""

echo "CJID=\$(sbatch ${SB_ARGS} ${SB_EXPORT} ${PROG} ${PROG_ARG})" >> ${SBLOG};
CJID=$(sbatch ${SB_ARGS} ${SB_EXPORT} ${PROG} ${PROG_ARG});
CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;
echo "$CJID"

