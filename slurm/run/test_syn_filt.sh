#!/bin/bash

source ../env/set_base_project_env.sh;

JNAME="syn_filter_trim";
OLOG="../logs/t1b_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="../logs/t1b_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../N_iter/1b_syn_filter_trim_traces.slurm";

CJID=$(./spec_sbatch.sh -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG);

CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;
echo $CJID;
