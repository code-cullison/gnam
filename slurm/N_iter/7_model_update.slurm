#!/bin/bash

echo `date`;

echo;
echo "SLURM_JOB_ID=$SLURM_JOB_ID";
echo "squeue -j $SLURM_JOB_ID:";
echo "$(squeue -j ${SLURM_JOB_ID})";
echo;

echo "pwd";
echo `pwd`;
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
export OF_DIR="${EVENT_DIR}/OUTPUT_FILES"
export DB_MPI_DIR="${OF_DIR}/DATABASES_MPI"
export DATA_DIR="${EVENT_DIR}/DATA"
export IGRAD_DIR="${EVENT_DIR}/INPUT_GRADIENT"
export IMOD_DIR="${EVENT_DIR}/INPUT_MODEL"
export COMB_DIR="${EVENT_DIR}/COMBINE"

####################################################################################

# make vtk file for kernels
echo;
echo;
echo "Setting up kernel links";
echo;
echo "cd $EVENT_DIR;"
cd $EVENT_DIR;
echo;
echo;
#Setup links
ALPH_CMD="ls $COMB_DIR/proc*_alpha_kernel.bin" 
BETA_CMD="ls $COMB_DIR/proc*_beta_kernel.bin" 
RHO_CMD="ls $COMB_DIR/proc*_rho_kernel.bin" 
XARG_CMD="xargs -t -P0 -I {} ln -srf $COMB_DIR/{}.bin $IGRAD_DIR/{}_smooth.bin"
echo "${ALPH_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}";
echo `${ALPH_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}`;
echo "${BETA_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}";
echo `${BETA_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}`;
echo "${RHO_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}";
echo `${RHO_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}`;
echo;
echo;
echo "Setting up previous model links";
echo;
VP_CMD="ls $DB_MPI_DIR/proc*_vp.bin"
VS_CMD="ls $DB_MPI_DIR/proc*_vs.bin"
RH_CMD="ls $DB_MPI_DIR/proc*_rho.bin"
XARG_CMD="xargs -t -P0 -I {} ln -srf $DB_MPI_DIR/{} $IMOD_DIR/{}"
echo "${VP_CMD} | rev | cut -d '/' -f1 | rev | ${XARG_CMD}";
echo `${VP_CMD} | rev | cut -d '/' -f1 | rev | ${XARG_CMD}`;
echo "${VS_CMD} | rev | cut -d '/' -f1 | rev | ${XARG_CMD}";
echo `${VS_CMD} | rev | cut -d '/' -f1 | rev | ${XARG_CMD}`;
echo "${RH_CMD} | rev | cut -d '/' -f1 | rev | ${XARG_CMD}";
echo `${RH_CMD} | rev | cut -d '/' -f1 | rev | ${XARG_CMD}`;
echo;
echo;
echo "Summing Preconditioned Kernel Subdomains...";
echo;

STEP_FACTOR=$1

echo "$MPIRUN ./bin/xadd_model_iso $STEP_FACTOR";
$MPIRUN ./bin/xadd_model_iso $STEP_FACTOR;
echo;


echo;
echo "ls $DATA_DIR/Par_file";
ls $DATA_DIR/Par_file;
echo "cp $DATA_DIR/Par_file $DATA_DIR/model_update.Par_file";
cp $DATA_DIR/Par_file $DATA_DIR/model_update.Par_file;
echo "Done..."
echo "See results in directory: OUTPUT_MODEL/"
echo `date`
