#!/bin/bash
####################################################################################
echo `date`;

NPROC=$1 #passed as an argument because only on cpu is needed but NPROC domains

#get project env and setup modules
echo "source ../env/set_base_project_env.sh";
source ../env/set_base_project_env.sh;
echo "source ../env/set_project_modules.sh";
source ../env/set_project_modules.sh;

#set local project dir names
export EVENT_DIR="${SPEC_PROJ_DIR}/run0001"
export OF_DIR="${EVENT_DIR}/OUTPUT_FILES"
export DB_MPI_DIR="${OF_DIR}/DATABASES_MPI"
export DATA_DIR="${EVENT_DIR}/DATA"
export MESH_DIR="${SPEC_PROJ_DIR}/MESH-default";

echo;
echo "SLURM_JOB_ID=$SLURM_JOB_ID";
echo "squeue -j $SLURM_JOB_ID:";
echo "$(squeue -j ${SLURM_JOB_ID})";
echo;


####################################################################################

echo;
echo "  decomposing mesh...";
echo;
echo "cd $EVENT_DIR;";
cd $EVENT_DIR;
echo;
echo "./bin/xdecompose_mesh $NPROC $MESH_DIR $DB_MPI_DIR";
./bin/xdecompose_mesh $NPROC $MESH_DIR $DB_MPI_DIR;

# checks exit code
if [[ $? -ne 0 ]]; then 
  echo;
  echo "There was an error running xdecompose_mesh";
  exit 1; 
else
  echo;
  echo "xdecompose_mesh completed successfully";
fi

##*****************************************##

echo;
echo "cp $DATA_DIR/Par_file $DATA_DIR/decomp_mesh.Par_file";
cp $DATA_DIR/Par_file $DATA_DIR/decomp_mesh.Par_file;
echo "Done..."
echo "See results in directory: $DB_MPI_DIR/"
echo `date`;
