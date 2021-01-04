#!/bin/bash

THISNAME=`echo $0 | rev | cut -d '/' -f1 | cut -d '.' -f2 | rev | cut -d '_' -f2,3`;

###########################################
#
# Read arguments
#
###########################################


SPEC_ARCH="CPU"
SPEC_NPROC=1
SPEC_ITER=0
LOG_PATH="./"
NPU=""
PJID=""
CUR_ITER_NUM=0

for i in "$@"; do
  case $i in
    -nCPU=*)
    SPEC_NPROC="${i#*=}"
    NPU="-nCPU=$SPEC_NPROC"
    NCPU="SET"
    ;;
    -nGPU=*)
    SPEC_NPROC="${i#*=}"
    SPEC_ARCH="GPU"
    NPU="-nGPU=$SPEC_NPROC"
    NGPU="SET"
    ;;
    -lp=*)
    LOG_PATH="${i#*=}"
    ;;
    -w=*)
    PJID="${i#*=}"
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

LDATE=`date +.on.%F.at.%H:%M:%S`
RLOG="${LOG_PATH}${THISNAME}${LDATE}.rlog"

echo "source ../env/set_base_project_env.sh" >> $RLOG;
source ../env/set_base_project_env.sh;

BASE_EVENT_DIR=${SPEC_PROJ_DIR}/run0001
CUR_ITER_FILE=$BASE_EVENT_DIR/current_iteration.sh
if [ -f "$CUR_ITER_FILE" ]; then
  echo "source $CUR_ITER_FILE" >> $RLOG;
  echo "Current Iteration: $CUR_ITER_NUM" >> $RLOG;
  source $CUR_ITER_FILE;
else 
  echo "$CUR_ITER_FILE does not exist.";
  exit 2;
fi


###########################################
#
# Step-2: Create adjoint sources
#
###########################################
if [[ ! -z $PJID ]]; then
  FCJID="-w=afterok:$PJID";
fi

JNAME="create_adj_srcs";
PROG="../N_iter/2_create_adj_srcs.slurm";

declare -A adj_jobid_array

for dir in ${SPEC_PROJ_DIR}/run[0-9][0-9][0-9][0-9]/; do
  RDIR=`echo "$dir" | rev | cut -d '/' -f2 | rev` >> $RLOG
  OLOG="t2_${JNAME}_$RDIR.job.%N.%j.out"  #STDOUT Log
  ELOG="t2_${JNAME}_$RDIR.job.%N.%j.err"  #STDERR Log
  echo "CJID=\$(./spec_sbatch.sh $FCJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa=$RDIR)" >> $RLOG;
  TJID=$(./spec_sbatch.sh $FCJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa=$RDIR);
  echo "SLURM JOBID: $TJID" >> $RLOG;
  TJID=`echo ${TJID} | rev | cut -d ' ' -f1 | rev`;
  adj_jobid_array+=([$RDIR]=$TJID)
done
STR=${adj_jobid_array[@]};
CJID=`echo ${STR// /:}`; #concatenated jobs with ':' for delimeters


################################################################
#
# Final-Step: echo SLURM Job ID's still to be waited on.
#
################################################################
echo $CJID
