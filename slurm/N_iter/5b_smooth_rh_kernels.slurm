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
export IKER_DIR="${EVENT_DIR}/INPUT_KERNELS/event0001"

####################################################################################

# make vtk file for kernels
echo;
echo;
echo "Smoothing Kernel Subdomains...";
echo;
echo "cd $EVENT_DIR;"
cd $EVENT_DIR;
echo;

SIG_H=1000
SIG_V=1000
IDIR=$EVENT_DIR/COMBINE
ODIR=$EVENT_DIR/SMOOTH

echo "$MPIRUN ./bin/xsmooth_sem $SIG_H $SIG_V rho_kernel $IDIR $ODIR true"; 
$MPIRUN ./bin/xsmooth_sem $SIG_H $SIG_V rho_kernel $IDIR $ODIR true; 
echo;
#echo "$MPIRUN ./bin/xsmooth_sem $SIG_H $SIG_V rho_kernel_clip $IDIR $ODIR true"; 
#$MPIRUN ./bin/xsmooth_sem $SIG_H $SIG_V rho_kernel_clip $IDIR $ODIR true; 
#echo;

echo "$MPIRUN ./bin/xsmooth_sem $SIG_H $SIG_V hess_kernel $IDIR $ODIR true"; 
$MPIRUN ./bin/xsmooth_sem $SIG_H $SIG_V hess_kernel $IDIR $ODIR true; 
echo;
#echo "$MPIRUN ./bin/xsmooth_sem $SIG_H $SIG_V hess_kernel_clip $IDIR $ODIR true"; 
#$MPIRUN ./bin/xsmooth_sem $SIG_H $SIG_V hess_kernel_clip $IDIR $ODIR true; 
#echo;
echo;
echo;
# Setup links for the preconditioning
RHO_CMD="ls $ODIR/proc*_rho_kernel_smooth.bin" 
HESS_CMD="ls $ODIR/proc*_hess_kernel_smooth.bin" 
XARG_CMD="xargs -t -P0 -I {} ln -srf $ODIR/{}_smooth.bin $IKER_DIR/{}.bin"
echo "${RHO_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | cut -d '_' -f1-3 | ${XARG_CMD}";
echo `${RHO_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | cut -d '_' -f1-3 | ${XARG_CMD}`;
echo "${HESS_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | cut -d '_' -f1-3 | ${XARG_CMD}";
echo `${HESS_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | cut -d '_' -f1-3 | ${XARG_CMD}`;
echo;
echo;
echo;
echo;
echo "ls $DATA_DIR/Par_file";
ls $DATA_DIR/Par_file;
echo "cp $DATA_DIR/Par_file $DATA_DIR/smooth_kern_rh.Par_file";
cp $DATA_DIR/Par_file $DATA_DIR/smooth_kern_rh.Par_file;
echo "Done..."
echo "See results in directory: OUTPUT_FILES/"
echo;
echo `date`
