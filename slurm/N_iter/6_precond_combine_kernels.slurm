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
export IKERN_DIR="${EVENT_DIR}/INPUT_KERNELS"


####################################################################################

# make vtk file for kernels
echo;
echo;
echo "Summing Preconditioned Kernel Subdomains...";
echo;
echo "cd $EVENT_DIR;"
cd $EVENT_DIR;
echo;

#Make the link and kernels_list.txt
echo "echo event0001 > kernels_list.txt";
echo "event0001" > kernels_list.txt;
echo "ln -srf $EVENT_DIR/SMOOTH $IKERN_DIR/event0001";
ln -srf $EVENT_DIR/SMOOTH $IKERN_DIR/event0001;
echo;


echo "$MPIRUN ./bin/xsum_preconditioned_kernels";
$MPIRUN ./bin/xsum_preconditioned_kernels;


echo;
echo "ls $DATA_DIR/Par_file";
ls $DATA_DIR/Par_file;
echo "cp $DATA_DIR/Par_file $DATA_DIR/precond_combine.Par_file";
cp $DATA_DIR/Par_file $DATA_DIR/precond_combine.Par_file;
echo "Done..."
echo "See results in directory: OUTPUT_FILES/"
echo `date`
