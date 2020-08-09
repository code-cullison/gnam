#!/bin/bash

JNAME="next_gen_db_mpi";
OLOG="../logs/t9_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="../logs/t9_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../N_iter/9_generate_databases.slurm";

echo $(sbatch -n 12 -N 12 --ntasks-per-node=1 --threads-per-core=1 --partition=gpu --gres=gpu --exclusive -o $OLOG -e $ELOG -J $JNAME --export=ALL,SPEC_ARCH=GPU,SPEC_NPROC=12 $PROG);
