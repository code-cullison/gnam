#!/bin/bash

source ../env/set_base_project_env.sh;

JNAME="post_smooth_alpha_kernel";
OLOG="../logs/t_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="../logs/t_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../post_process/smooth_alpha_kernel.slurm";

CJID=$(./spec_sbatch.sh -nGPU=4 -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG);

CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;
echo $CJID;
