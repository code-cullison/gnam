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
export IDIR="${SPEC_PROJ_DIR}/run0001/SMOOTH"
export ODIR="${SPEC_PROJ_DIR}/run0001/OUTPUT_SUM"


####################################################################################

# make vtk file for kernels
echo;
echo;
echo "Soft link clipped and smoothed kenels to OUTPUT_SUM...";
echo;
echo "cd $EVENT_DIR;"
cd $EVENT_DIR;
echo;


ALPH_CMD="ls $IDIR/proc*_alpha_kernel.bin"
BETA_CMD="ls $IDIR/proc*_beta_kernel.bin"
RHO_CMD="ls $IDIR/proc*_rho_kernel.bin"
XARG_CMD="xargs -t -P0 -I {} ln -srf $IDIR/{} $ODIR/{}"
echo "${ALPH_CMD} | rev | cut -d '/' -f1 | rev | ${XARG_CMD}";
echo `${ALPH_CMD} | rev | cut -d '/' -f1 | rev | ${XARG_CMD}`;
echo "${BETA_CMD} | rev | cut -d '/' -f1 | rev | ${XARG_CMD}";
echo `${BETA_CMD} | rev | cut -d '/' -f1 | rev | ${XARG_CMD}`;
echo "${RHO_CMD} | rev | cut -d '/' -f1 | rev | ${XARG_CMD}";
echo `${RHO_CMD} | rev | cut -d '/' -f1 | rev | ${XARG_CMD}`;


echo;
echo "ls $DATA_DIR/Par_file";
ls $DATA_DIR/Par_file;
echo "cp $DATA_DIR/Par_file $DATA_DIR/precond_combine.Par_file";
cp $DATA_DIR/Par_file $DATA_DIR/precond_combine.Par_file;
echo "Done..."
echo "See results in directory: OUTPUT_SUM/"
echo `date`
