#!/bin/bash

echo $(sbatch -n 12 -N 12 --ntasks-per-node=1 --threads-per-core=1 --partition=gpu --gres=gpu --exclusive -o ../logs/t7_model_update.job.%N.%j.out -e ../logs/t7_model_update.job.%N.%j.err -J model_update --export=ALL,SPEC_ARCH=GPU,SPEC_NPROC=12 ../N_iter/7_model_update.slurm 0.5);
