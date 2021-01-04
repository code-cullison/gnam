#!/bin/bash

source ../env/set_base_project_env.sh;

JNAME="symlinks_4_precond";
OLOG="t6.5_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="t6.5_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../N_iter/t6.5_symlinks_4_precondition.slurm";

CJID=$(./spec_sbatch.sh -nGPU=1 -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG);

CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;
echo $CJID;
