#!/bin/bash

SVAL=$1

####################################################################################

#setup job env
echo "source ../env/set_base_project_env.sh";
source ../env/set_base_project_env.sh;

EVENT_DIR="${SPEC_PROJ_DIR}/run0001"
DATA_DIR="${EVENT_DIR}/DATA"

####################################################################################

TPFILE="${DATA_DIR}/Par_file"
echo "sed -e "/^MODEL/ s/\= .*/\= $SVAL/g" < ${TPFILE} > ${DATA_DIR}/tmp_Parfile"; 
sed -e "/^MODEL/ s/\=.*/\= $SVAL/g" < ${TPFILE} > ${DATA_DIR}/tmp_Parfile; 
echo "mv ${DATA_DIR}/tmp_Parfile $TPFILE";
mv ${DATA_DIR}/tmp_Parfile $TPFILE;
echo;
echo "Done"
echo;
echo `date`;

####################################################################################
