#!/bin/bash

JNAME="prepair_next_iter";
OLOG="../logs/t8_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="../logs/t8_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../N_iter/8_prepair_next_iter.slurm";

echo $(sbatch -n 12 -N 12 --ntasks-per-node=1 --threads-per-core=1 --partition=gpu --gres=gpu --exclusive -o $OLOG -e $ELOG -J $JNAME --export=ALL,SPEC_ARCH=GPU,SPEC_NPROC=12 $PROG 0.5);
