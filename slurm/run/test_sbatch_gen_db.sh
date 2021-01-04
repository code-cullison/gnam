#!/bin/bash
source ../env/set_base_project_env.sh;
CJID=$(sbatch -n 2 -N 1 --nodelist=gpu039 --ntasks-per-node=2 --threads-per-core=1 --partition=allq --gres=gpu:gtx1080ti:2 --exclusive -o ../logs/1_gen_db_mpi.job.%N.%j.out -e ../logs/1_gen_db_mpi.job.%N.%j.err -J gen_db_mpi --export=ALL,SPEC_ARCH=GPU,SPEC_NPROC=2 ../0_iter/1_generate_databases.slurm );
