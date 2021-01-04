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
export EVENT_DIR="${SPEC_PROJ_DIR}/$1"
export OF_DIR="${EVENT_DIR}/OUTPUT_FILES"
export DATA_DIR="${EVENT_DIR}/DATA"

####################################################################################

# This is a MPI simulation
echo;
echo "Running adjoint-kernels solver for $1 using $SPEC_NPROC processors..."
echo;
echo "cd $EVENT_DIR;"
cd $EVENT_DIR;
echo;
echo "module list";
module list;
echo;
echo "./utils/change_simulation_type.pl -b"; #adj + forward no save
./utils/change_simulation_type.pl -b;
echo;
echo "$MPIRUN ./bin/xspecfem3D;";
$MPIRUN ./bin/xspecfem3D;

# checks exit code
if [[ $? -ne 0 ]]; then 
  echo;
  echo "There was an error changing the simulation type";
  exit 1; 
else
  echo;
  echo "Simulation type changed successfully";
fi


##*****************************************##

# Rename Last Timestamp

echo;
TOMODIR="${SPEC_PROJ_DIR}/run0001"
ITERNUM=$(cat ${TOMODIR}/current_iteration.sh | grep CUR_ITER_NUM | cut -d '=' -f2)
echo "\\ls $OF_DIR/timestamp0* | tail -1 | rev | cut -d '/' -f1 | rev | xargs -t -P0 -I {} cp $OF_DIR/{} $OF_DIR/adj.iter_${ITERNUM}.{}";
\ls $OF_DIR/timestamp0* | tail -1 | rev | cut -d '/' -f1 | rev | xargs -t -P0 -I {} cp $OF_DIR/{} $OF_DIR/adj.iter_${ITERNUM}.{};
echo;

# checks exit code
if [[ $? -ne 0 ]]; then 
  echo;
  echo "There was an error copying the timestamp";
  exit 1; 
else
  echo;
  echo "Timestamp copy completed successfully";
fi


##*****************************************##

# Save Par_file for record keeping

echo
echo "ls $DATA_DIR/Par_file";
ls $DATA_DIR/Par_file;
echo "cp $DATA_DIR/Par_file $DATA_DIR/adj_kernels.Par_file";
cp $DATA_DIR/Par_file $DATA_DIR/adj_kernels.Par_file;
echo;
echo "./utils/change_simulation_type.pl -F"; #forward + save
./utils/change_simulation_type.pl -F;
echo;
echo "Done..."
echo "See results in directory: OUTPUT_FILES/"
echo `date`
