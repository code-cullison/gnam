#!/bin/bash

THISNAME=`echo $0 | rev | cut -d '/' -f1 | cut -d '.' -f2 | rev | cut -d '_' -f2,3`;

###########################################
#
# Read arguments
#
###########################################

SPEC_ARCH="CPU"
SPEC_NPROC=1
LOG_PATH="./"
NPU=""
PJID=""

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

###########################################
#
# Step-0: Decompose Mesh
#
###########################################

##------- First: Set SAVE_MESH = .true. -------##


if [[ ! -z $PJID ]]; then
  PJID="-w=afterok:$PJID";
fi

JNAME="save_mesh_eq_true";
OLOG="parfile_0_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="parfile_0_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../parfile/change_save_mesh.sh";

#Note: that NPU is NOT passed as an argument
echo "CJID=\$(./spec_sbatch.sh $PJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa="true")" >> $RLOG;
CJID=$(./spec_sbatch.sh $PJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa="true");

echo "SLURM JOBID: $CJID" >> $RLOG;
CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;


##------- Second: Set NPROC = $SPEC_NPROC -------##

CJID="afterok:$CJID";

JNAME="chang_nrpoc";
OLOG="parfile_0_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="parfile_0_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../parfile/change_nproc.sh";

#Note: that NPU is NOT passed as an argument
echo "CJID=\$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa="true")" >> $RLOG;
CJID=$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa=$SPEC_NPROC);

echo "SLURM JOBID: $CJID" >> $RLOG;
CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;


##------- Third: Set MODEL = default -------##

CJID="afterok:$CJID";

JNAME="chang_model";
OLOG="parfile_0_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="parfile_0_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../parfile/change_model.sh";

#Note: that NPU is NOT passed as an argument
echo "CJID=\$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa="true")" >> $RLOG;
CJID=$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa="default");

echo "SLURM JOBID: $CJID" >> $RLOG;
CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;


##------- Decompose Mesh  ---------------------##

CJID="afterok:$CJID";

JNAME="decomp_mesh";
OLOG="0_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="0_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../0_iter/0_decompose_mesh.slurm";

#Note: that NPU is NOT passed, instead NPROC is as a prog argument
echo "CJID=\$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa=$SPEC_NPROC)" > $RLOG;
CJID=$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa=$SPEC_NPROC);

echo "SLURM JOBID: $CJID" >> $RLOG;
CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;


################################################################
#
# Final-Step: echo SLURM Job ID's still to be waited on.
#
################################################################
echo "$CJID"
