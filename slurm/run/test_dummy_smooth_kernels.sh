#!/bin/bash

source ../env/set_base_project_env.sh;

JNAME="dummy_ab_kernels";
OLOG="5a_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="5a_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../N_iter/5a_dummy_smooth_ab_kernels.slurm";

CJID=$(./spec_sbatch.sh -w="afterok:3228676" -nGPU=2 -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG);

CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;

SJID=$CJID;

JNAME="dummy_rh_kernels";
OLOG="5b_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="5b_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../N_iter/5b_dummy_smooth_rh_kernels.slurm";

#Note: that $NJID is used INSTEAD of $CJID
CJID=$(./spec_sbatch.sh -w="afterok:3228676" -nGPU=2 -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG);

echo "SLURM JOBID: $CJID" >> $RLOG;
CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;
CJID="$SJID:$CJID";

echo $CJID;
