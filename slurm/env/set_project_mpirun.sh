#!/bin/bash

MYARCH=$SPEC_ARCH
NPROC=$SPEC_NPROC
MONE_NPROC=`expr $NPROC - 1`;

if [[ $MYARCH == "CPU" ]]; then
  echo "export MPIRUN=mpirun -np $NPROC -genv I_MPI_PIN_PROCESSOR_LIST=0-$MONE_NPROC -genv I_MPI_FABRICS=shm:ofa ";
  export MPIRUN="mpirun -np $NPROC -genv I_MPI_PIN_PROCESSOR_LIST=0-$MONE_NPROC -genv I_MPI_FABRICS=shm:ofa ";
fi

if [[ $MYARCH == "GPU" ]]; then
  echo "export MPIRUN=mpirun -np $NPROC --mca btl_openib_cuda_rdma_limit 100000 ";
  export MPIRUN="mpirun -np $NPROC --mca btl_openib_cuda_rdma_limit 100000 ";
fi
