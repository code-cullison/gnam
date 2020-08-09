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
echo "Combining Kernel Subdomains from all events...";
echo;
echo "cd $EVENT_DIR;"
cd $EVENT_DIR;
echo;
echo "make event_kernel_dirs.txt";
cat > event_kernel_dirs.txt <<EOF
OUTPUT_FILES/DATABASES_MPI/
../run0002/OUTPUT_FILES/DATABASES_MPI/
../run0003/OUTPUT_FILES/DATABASES_MPI/
EOF
echo "cat event_kernel_dirs.txt";
cat event_kernel_dirs.txt;

IFILE=event_kernel_dirs.txt
KNAME=alpha_kernel,beta_kernel,rho_kernel,hess_kernel
ODIR="$EVENT_DIR/COMBINE"

echo "$MPIRUN ./bin/xcombine_sem $KNAME $IFILE $ODIR";
$MPIRUN ./bin/xcombine_sem $KNAME $IFILE $ODIR;
echo;


echo "ls $DATA_DIR/Par_file";
ls $DATA_DIR/Par_file;
echo "cp $DATA_DIR/Par_file $DATA_DIR/combine_sem.Par_file";
cp $DATA_DIR/Par_file $DATA_DIR/combine_sem.Par_file;
echo "Done..."
echo "See results in directory: OUTPUT_FILES/"
echo `date`
