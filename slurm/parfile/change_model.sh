#!/bin/bash

SVAL=$1

####################################################################################

#setup job env
echo "source ../env/set_base_project_env.sh";
source ../env/set_base_project_env.sh;

EVENT_DIR="${SPEC_PROJ_DIR}/run0001"
DATA_DIR="${EVENT_DIR}/DATA"

####################################################################################

for dir in ${SPEC_PROJ_DIR}/run[0-9][0-9][0-9][0-9]/; do
  TPFILE="$dir/DATA/Par_file"
  DATA_DIR="${dir}/DATA"
  echo "sed -e "/^MODEL/ s/\= .*/\= $SVAL/g" < ${TPFILE} > ${DATA_DIR}/tmp_Parfile"; 
  sed -e "/^MODEL/ s/\=.*/\= $SVAL/g" < ${TPFILE} > ${DATA_DIR}/tmp_Parfile; 
  echo "mv ${DATA_DIR}/tmp_Parfile $TPFILE";
  mv ${DATA_DIR}/tmp_Parfile $TPFILE;
  echo;
done

echo "Done"
echo;
echo `date`;

####################################################################################
