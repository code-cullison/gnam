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
export OF_DIR="${EVENT_DIR}/OUTPUT_FILES"
export DB_MPI_DIR="${OF_DIR}/DATABASES_MPI"
export DATA_DIR="${EVENT_DIR}/DATA"


####################################################################################

# This creates the databases (via MPI)
echo;
echo "  running database generation on $NPROC processors..."
echo;
echo "cd $EVENT_DIR;"; 
cd $EVENT_DIR;
echo;
echo "pwd";
echo `pwd`;
echo 'which mpirun';
echo `which mpirun`;
echo;
echo "$MPIRUN ./bin/xgenerate_databases";
$MPIRUN ./bin/xgenerate_databases;

# checks exit code
if [[ $? -ne 0 ]]; then 
  echo;
  echo "There was an error running xgenerate_databases";
  exit 1; 
else
  echo;
  echo "xgenerate_databases completed successfully";
fi

####################################################################################

echo;
echo "cp $DATA_DIR/Par_file $DATA_DIR/gen_db.Par_file";
cp $DATA_DIR/Par_file $DATA_DIR/gen_db.Par_file;
echo "Done..."
echo "See results in directory: $DB_MPI_DIR/"
echo `date`;
