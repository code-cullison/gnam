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
NITER="1"

for i in "$@"; do
  case $i in
    -niter=*)
    NITER="${i#*=}"
    ;;
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
# Step-0: Set
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
echo "CJID=\$(./spec_sbatch.sh -$PJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa="true")" >> $RLOG;
CJID=$(./spec_sbatch.sh $PJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa="true");

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


###########################################
#
# Step-1: Generate Databases (MPI)
#
###########################################
CJID="afterok:$CJID";

JNAME="gen_db_mpi";
OLOG="1_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="1_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../0_iter/1_generate_databases.slurm";

#Note: that NPU IS passed as and argument
echo "CJID=\$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG $NPU -lp=$LOG_PATH -jn=$JNAME -x=$PROG)" >> $RLOG;
CJID=$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG $NPU -lp=$LOG_PATH -jn=$JNAME -x=$PROG);

echo "SLURM JOBID: $CJID" >> $RLOG;
CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;


###########################################
#
# Step-2: Create links to Databases
#
###########################################
CJID="afterok:$CJID";

JNAME="create_db_links";
OLOG="2_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="2_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../0_iter/2_create_db_mpi_links.slurm";

#Note: that NPU is NOT passed as and argument
echo "CJID=\$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG)" >> $RLOG;
CJID=$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG);

echo "SLURM JOBID: $CJID" >> $RLOG;
CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;


################################################################
#
# Final-Step: echo SLURM Job ID's still to be waited on.
#
################################################################
echo "$CJID"
