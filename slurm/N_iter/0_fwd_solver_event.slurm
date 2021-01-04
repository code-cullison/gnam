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
export SYN_DIR="${EVENT_DIR}/SYN"

####################################################################################

# set NPROC in Par_file

TPFILE="${DATA_DIR}/Par_file"
echo "sed -e "s#^NPROC.*#NPROC = $SPEC_NPROC #g" < $TPFILE > ${DATA_DIR}/tmp_Parfile"; 
sed -e "s#^NPROC.*#NPROC = $SPEC_NPROC #g" < $TPFILE > ${DATA_DIR}/tmp_Parfile; 

echo "mv ${DATA_DIR}/tmp_Parfile $TPFILE";
mv ${DATA_DIR}/tmp_Parfile $TPFILE;

echo "grep -e 'NPROC' "$DATA_DIR/Par_file" | head -1";
grep -e 'NPROC' "$DATA_DIR/Par_file" | head -1;

####################################################################################

# This is a MPI simulation
echo;
echo "Running solver for $1 using $SPEC_NPROC processors..."
echo;
echo "cd $EVENT_DIR;"
cd $EVENT_DIR;
echo;
echo "./utils/change_simulation_type.pl -F"; #forward with save
./utils/change_simulation_type.pl -F;
echo;
echo "$MPIRUN ./bin/xspecfem3D;";
$MPIRUN ./bin/xspecfem3D;

# checks exit code
if [[ $? -ne 0 ]]; then 
  echo;
  echo "There was an error running xspecfem3D";
  exit 1; 
else
  echo;
  echo "xspecfem3D completed successfully";
fi

##*****************************************##

# Move data in OUTPUT_FILES to SYN 

echo;
echo "mv $OF_DIR/*.semd $SYN_DIR";
mv $OF_DIR/*.semd $SYN_DIR;
echo;

# checks exit code
if [[ $? -ne 0 ]]; then 
  echo;
  echo "There was an error moving the .semd files";
  exit 1; 
else
  echo;
  echo "moving of .semd files completed successfully";
fi


##*****************************************##

# Rename Last Timestamp

echo;
TOMODIR="${SPEC_PROJ_DIR}/run0001"
ITERNUM=$(cat ${TOMODIR}/current_iteration.sh | grep CUR_ITER_NUM | cut -d '=' -f2)
echo "\\ls $OF_DIR/timestamp0* | tail -1 | rev | cut -d '/' -f1 | rev | xargs -t -P0 -I {} cp $OF_DIR/{} $OF_DIR/fwd.iter_${ITERNUM}.{}";
\ls $OF_DIR/timestamp0* | tail -1 | rev | cut -d '/' -f1 | rev | xargs -t -P0 -I {} cp $OF_DIR/{} $OF_DIR/fwd.iter_${ITERNUM}.{};
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
echo "cp $DATA_DIR/Par_file $DATA_DIR/fwd_solver.Par_file";
cp $DATA_DIR/Par_file $DATA_DIR/fwd_solver.Par_file;
echo "Done..."
echo "See results in directory: OUTPUT_FILES/"
echo `date`
