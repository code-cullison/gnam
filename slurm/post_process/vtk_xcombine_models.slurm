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
echo "Computing VTK file for model(s)";
echo;
echo "cd $EVENT_DIR;"
cd $EVENT_DIR;
echo;

VP=vp
#VP=vp_iter_3
VS=vs
RHO=rho

IDIR=$EVENT_DIR/OUTPUT_FILES/DATABASES_MPI
ODIR=$IDIR

echo "./bin/xcombine_vol_data_vtk 0 $MONE_NPROC $VP $IDIR $ODIR 0";
./bin/xcombine_vol_data_vtk 0 $MONE_NPROC $VP $IDIR $ODIR 0;
echo;

#echo "./bin/xcombine_vol_data_vtk 0 $MONE_NPROC $VS $IDIR $ODIR 0";
#./bin/xcombine_vol_data_vtk 0 $MONE_NPROC $VS $IDIR $ODIR 0;
#echo;

#echo "./bin/xcombine_vol_data_vtk 0 $MONE_NPROC $RHO $IDIR $ODIR 0";
#./bin/xcombine_vol_data_vtk 0 $MONE_NPROC $RHO $IDIR $ODIR 0;
#echo;


echo;
echo "Done..."
echo "See results in directory: $ODIR"
echo `date`
