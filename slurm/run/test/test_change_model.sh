#!/bin/bash

JNAME="change_model_gll";
OLOG="../logs/tparfile_9_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="../logs/tparfile_9_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../parfile/change_model.sh";

echo $(sbatch -n 12 -N 12 --ntasks-per-node=1 --threads-per-core=1 --partition=gpu --gres=gpu --exclusive -o $OLOG -e $ELOG -J $JNAME --export=ALL,SPEC_ARCH=GPU,SPEC_NPROC=12 $PROG "gll");

