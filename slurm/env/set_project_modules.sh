#!/bin/bash

MYARCH=$SPEC_ARCH

if [[ $MYARCH == GPU ]]; then
  echo "Setting GPU modules"
  echo;
  echo "module purge";
  module purge;
  echo "module load userspace/all opt/all";
  module load userspace/all opt/all;
  echo "module load cuda/8.0 gcc/5.5.0 openmpi/gcc-5.5.0/3.1.2";
  module load cuda/8.0 gcc/5.5.0 openmpi/gcc-5.5.0/3.1.2;
  echo "module list";
  module list;
  echo;
elif [[ $MYARCH == CPU ]]; then
  echo "Setting CPU modules"
  echo;
  echo "module purge";
  module purge;
  echo "module load userspace/custom";
  module load userspace/custom;
  echo "module load intel-compiler/64/2018.3.222 intel-mpi/64/2018.3.222 intel-mkl/64/2018.3.222";
  module load intel-compiler/64/2018.3.222 intel-mpi/64/2018.3.222 intel-mkl/64/2018.3.222;
  echo "module list";
  module list;
  echo;
else
  echo "Module setup failed. SPEC_ARCH=$MYARCH";
  exit 1;
fi

