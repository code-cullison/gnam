#!/bin/bash

echo `date`;


echo;
echo "SLURM_JOB_ID=$SLURM_JOB_ID";
echo "squeue -j $SLURM_JOB_ID:";
echo "$(squeue -j ${SLURM_JOB_ID})";
echo;

####################################################################################

#setup job env
echo "source ../env/set_base_project_env.sh";
source ../env/set_base_project_env.sh;

#set BASE project dir names
BASE_EVENT_DIR="${SPEC_PROJ_DIR}/run0001"
BASE_OF_DIR="${BASE_EVENT_DIR}/OUTPUT_FILES"
BASE_DB_MPI_DIR="${BASE_OF_DIR}/DATABASES_MPI"

####################################################################################

echo;
echo "Creating Database links";
echo;
echo;

####################################################
#
# First: make db and mesh links for each event directory
#
####################################################

for dir in ${SPEC_PROJ_DIR}/run[0-9][0-9][0-9][0-9]/; do
  RDIR=`echo "$dir" | rev | cut -d '/' -f2 | rev`
  if [[ $RDIR == "run0001" ]]; then
    continue
  fi
  LOC_OF_DIR="$dir/OUTPUT_FILES";
  LOC_DB_MPI_DIR="$LOC_OF_DIR/DATABASES_MPI";
  echo;
  # remove old mesh and db links #FIXME: shouldn't cleanup here
  echo "rm $LOC_DB_MPI_DIR/proc*external*.bin";
  rm $LOC_DB_MPI_DIR/proc*external*.bin;
  echo "rm $LOC_DB_MPI_DIR/proc*Database";
  rm $LOC_DB_MPI_DIR/proc*Database;
  echo;
  echo;
  # create new mesh and db links
  EM_CMD="ls $BASE_DB_MPI_DIR/proc*external*.bin"
  DB_CMD="ls $BASE_DB_MPI_DIR/proc*Database"
  XARG_CMD="xargs -t -P0 -I {} ln -srf $BASE_DB_MPI_DIR/{} $LOC_DB_MPI_DIR/{}"
  echo "${EM_CMD} | rev | cut -d '/' -f1 | rev | ${XARG_CMD}";
  echo `${EM_CMD} | rev | cut -d '/' -f1 | rev | ${XARG_CMD}`;
  echo "${DB_CMD} | rev | cut -d '/' -f1 | rev | ${XARG_CMD}";
  echo `${DB_CMD} | rev | cut -d '/' -f1 | rev | ${XARG_CMD}`;
  echo;
  echo;
  # make mesh header links 
  VM_CMD="ls $BASE_OF_DIR/values_from_mesher.h"
  SM_CMD="ls $BASE_OF_DIR/surface_from_mesher.h"
  XARG_CMD="xargs -t -P0 -I {} ln -srf $BASE_OF_DIR/{} $LOC_OF_DIR/{}"
  echo "${VM_CMD} | rev | cut -d '/' -f1 | rev | ${XARG_CMD}";
  echo `${VM_CMD} | rev | cut -d '/' -f1 | rev | ${XARG_CMD}`;
  echo "${SM_CMD} | rev | cut -d '/' -f1 | rev | ${XARG_CMD}";
  echo `${SM_CMD} | rev | cut -d '/' -f1 | rev | ${XARG_CMD}`;
  echo;
done

##########################################################
#
# Third: make mesh links for topo dir and model updates
#
##########################################################

EVENT_DIR="${SPEC_PROJ_DIR}/run0001"
OF_DIR="${EVENT_DIR}/OUTPUT_FILES"
DB_MPI_DIR="${OF_DIR}/DATABASES_MPI"
TOPO_DIR=${EVENT_DIR}/topo

MESH_CMD="ls $DB_MPI_DIR/proc*external_mesh.bin"
XARG_CMD="xargs -t -P0 -I {} ln -srf $DB_MPI_DIR/{} $TOPO_DIR/{}"
echo "${MESH_CMD} | rev | cut -d '/' -f1 | rev | ${XARG_CMD}";
echo `${MESH_CMD} | rev | cut -d '/' -f1 | rev | ${XARG_CMD}`;
echo;

##########################################################
#
# Fourth: create and set the current_iteration.sh
#
##########################################################

#CUR_ITER_NUM=0
#echo;
#echo "Creating $EVENT_DIR/current_iteration.sh";
#echo;
#echo "echo #!/bin/bash > $EVENT_DIR/current_iteration.sh";
#echo "#!/bin/bash" > $EVENT_DIR/current_iteration.sh;
#echo "echo CUR_ITER_NUM=$CUR_ITER_NUM >> $EVENT_DIR/current_iteration.sh";
#echo "CUR_ITER_NUM=$CUR_ITER_NUM" >> $EVENT_DIR/current_iteration.sh;
#echo;
#echo;
echo "Done..."
echo "See results in directory: $EVENT_DIR/"
echo `date`

#echo;
#cho "Finished Creating Database links";
#cho;
#cho `date`
