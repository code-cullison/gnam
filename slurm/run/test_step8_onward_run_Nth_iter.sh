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
# Step-0: Forward Solver
#
###########################################

JNAME="fwd_solver";
PROG="../N_iter/0_fwd_solver_event.slurm";

if [[ ! -z $PJID ]]; then
  PJID="-w=afterok:$PJID";
fi


###########################################################
#
# Step-8: Prepare Next Iteration
#
###########################################################

JNAME="prepair_next_iter";
OLOG="8_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="8_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../N_iter/8_prepair_next_iter.slurm";

#Note: that NPU is NOT passed as an argument
echo "CJID=\$(./spec_sbatch.sh $PJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG)" >> $RLOG;
CJID=$(./spec_sbatch.sh $PJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG);

echo "SLURM JOBID: $CJID" >> $RLOG;
CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;


###########################################################
#
# Step-9: Run Generate Databases for updated model
#
###########################################################

##------- Set MODEL = gll ---------------------##

if [[ $CUR_ITER_NUM == 0 ]]; then 
  CJID="afterok:$CJID";

  JNAME="change_model_gll";
  OLOG="parfile_9_${JNAME}.job.%N.%j.out";  # STDOUT
  ELOG="parfile_9_${JNAME}.job.%N.%j.err";  # STDERR
  PROG="../parfile/change_model.sh";

  #Note: that NPU is NOT passed as an argument
  echo "CJID=\$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa="gll")" >> $RLOG;
  CJID=$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa="gll");

  echo "SLURM JOBID: $CJID" >> $RLOG;
  CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;
fi

##------- Generate Databases ------------------##

CJID="afterok:$CJID";

JNAME="next_gen_db_mpi";
OLOG="9_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="9_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../N_iter/9_generate_databases.slurm";

echo "CJID=\$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG $NPU -lp=$LOG_PATH -jn=$JNAME -x=$PROG)" >> $RLOG;
CJID=$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG $NPU -lp=$LOG_PATH -jn=$JNAME -x=$PROG);

echo "SLURM JOBID: $CJID" >> $RLOG;
CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;


################################################################
#
# Final-Step: echo SLURM Job ID's still to be waited on.
#
################################################################
echo $CJID
