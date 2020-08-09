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
export DATA_DIR="${EVENT_DIR}/DATA"

####################################################################################

# make vtk file for kernels
echo;
echo;
echo "Smoothing Kernel Subdomains...";
echo;
echo "cd $EVENT_DIR;"
cd $EVENT_DIR;
echo;

SIG_H=250
SIG_V=250
IDIR=$EVENT_DIR/COMBINE
ODIR=$EVENT_DIR/SMOOTH

echo "$MPIRUN ./bin/xsmooth_sem $SIG_H $SIG_V alpha_kernel $IDIR $ODIR true"; 
$MPIRUN ./bin/xsmooth_sem $SIG_H $SIG_V alpha_kernel $IDIR $ODIR true; 
echo;

echo "$MPIRUN ./bin/xsmooth_sem $SIG_H $SIG_V beta_kernel $IDIR $ODIR true"; 
$MPIRUN ./bin/xsmooth_sem $SIG_H $SIG_V beta_kernel $IDIR $ODIR true; 
echo;


echo "ls $DATA_DIR/Par_file";
ls $DATA_DIR/Par_file;
echo "cp $DATA_DIR/Par_file $DATA_DIR/smooth_kern_ab.Par_file";
cp $DATA_DIR/Par_file $DATA_DIR/smooth_kern_ab.Par_file;
echo "Done..."
echo "See results in directory: OUTPUT_FILES/"
echo;
echo `date`
