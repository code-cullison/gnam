#!/bin/bash

echo `date`;

echo;
echo "SLURM_JOB_ID=$SLURM_JOB_ID";
echo "squeue -j $SLURM_JOB_ID:";
echo "$(squeue -j ${SLURM_JOB_ID})";
echo;

####################################################################################

#get project env and setup modules
echo "source ../env/set_base_project_env.sh";
source ../env/set_base_project_env.sh;
echo "source ../env/set_project_modules.sh";
source ../env/set_project_modules.sh;
echo "source ../env/set_project_mpirun.sh";
source ../env/set_project_mpirun.sh;

#set local project dir names
export EVENT_DIR="${SPEC_PROJ_DIR}/run0001"
#export EVENT_DIR="${SPEC_PROJ_DIR}/run0002"
#export EVENT_DIR="${SPEC_PROJ_DIR}/run0003"
export DATA_DIR="${EVENT_DIR}/DATA"


####################################################################################

# make vtk file for kernels
echo;
echo;
echo "Summing Preconditioned Kernel Subdomains...";
echo;
echo "cd $EVENT_DIR;"
cd $EVENT_DIR;
echo;

#KALPH=alpha_kernel
#KHESS=hess_kernel
#KHESS=hess_inv_kernel
#KALPH=alpha_kernel_smooth_iter_
KALPH=alpha_kernel_smooth_iter_0
#KALPH=alpha_kernel_clip
#KALPH=alpha_kernel_smooth
#KBETA=beta_kernel_smooth
#K_RHO=rho_kernel_smooth
#KHESS=hess_kernel_smooth_iter_9
IDIR=$EVENT_DIR/SMOOTH
#IDIR=$EVENT_DIR/OUTPUT_FILES/DATABASES_MPI
#IDIR=$EVENT_DIR/OUTPUT_SUM
#IDIR=$EVENT_DIR/INPUT_GRADIENT
#IDIR=$EVENT_DIR/COMBINE
ODIR=$IDIR

#echo "./bin/xcombine_vol_data_vtk 0 $MONE_NPROC ${KALPH}0 $IDIR $ODIR 0";
#./bin/xcombine_vol_data_vtk 0 $MONE_NPROC "${KALPH}0" $IDIR $ODIR 0;
#echo;

#echo "./bin/xcombine_vol_data_vtk 0 $MONE_NPROC ${KALPH}1 $IDIR $ODIR 0";
#./bin/xcombine_vol_data_vtk 0 $MONE_NPROC "${KALPH}1" $IDIR $ODIR 0;
#echo;

#echo "./bin/xcombine_vol_data_vtk 0 $MONE_NPROC ${KALPH}2 $IDIR $ODIR 0";
#./bin/xcombine_vol_data_vtk 0 $MONE_NPROC "${KALPH}2" $IDIR $ODIR 0;
#echo;

#echo "./bin/xcombine_vol_data_vtk 0 $MONE_NPROC ${KALPH}3 $IDIR $ODIR 0";
#./bin/xcombine_vol_data_vtk 0 $MONE_NPROC "${KALPH}3" $IDIR $ODIR 0;
#echo;

echo "./bin/xcombine_vol_data_vtk 0 $MONE_NPROC $KALPH $IDIR $ODIR 0";
./bin/xcombine_vol_data_vtk 0 $MONE_NPROC $KALPH $IDIR $ODIR 0;
echo;

#echo "./bin/xcombine_vol_data_vtk 0 $MONE_NPROC $KBETA $IDIR $ODIR 0";
#./bin/xcombine_vol_data_vtk 0 $MONE_NPROC $KBETA $IDIR $ODIR 0;
#echo;

#echo "./bin/xcombine_vol_data_vtk 0 $MONE_NPROC $K_RHO $IDIR $ODIR 0";
#./bin/xcombine_vol_data_vtk 0 $MONE_NPROC $K_RHO $IDIR $ODIR 0;
#echo;

#echo "./bin/xcombine_vol_data_vtk 0 $MONE_NPROC $KHESS $IDIR $ODIR 0";
#./bin/xcombine_vol_data_vtk 0 $MONE_NPROC $KHESS $IDIR $ODIR 0;
#echo;


echo;
echo "Done..."
echo "See results in directory: $ODIR"
echo `date`
