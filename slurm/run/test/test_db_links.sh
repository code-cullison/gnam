#!/bin/bash

source ../env/set_base_project_env.sh
echo $(sbatch -n 1 -N 1 --ntasks-per-node=1 --threads-per-core=1 --partition=allq  --exclusive -o ../logs/2_create_db_links.job.%N.%j.out -e ../logs/2_create_db_links.job.%N.%j.err -J create_db_links --export=ALL,SPEC_ARCH=CPU,SPEC_NPROC=1 ../0_iter/2_create_db_mpi_links.slurm)
