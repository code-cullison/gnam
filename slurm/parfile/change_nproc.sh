#!/bin/bash
####################################################################################

#setup job env
echo "source ../env/set_base_project_env.sh";
source ../env/set_base_project_env.sh;

####################################################################################

NPROC=$1


for dir in ${SPEC_PROJ_DIR}/run[0-9][0-9][0-9][0-9]/; do
  TPFILE="$dir/Data/Par_file"

  echo "\$sed -e s#^NPROC.*#NPROC = $NPROC #g < $TPFILE > ${DATA_DIR}/tmp_Parfile";
  $sed -e "s#^NPROC.*#NPROC = $NPROC #g" < $TPFILE > ${DATA_DIR}/tmp_Parfile; 

  echo "mv ${DATA_DIR}/tmp_Parfile $TPFILE";
  mv ${DATA_DIR}/tmp_Parfile $TPFILE;

  echo "grep -e 'NPROC' "$DATA_DIR/Par_file" | head -1";
  grep -e 'NPROC' "$DATA_DIR/Par_file" | head -1;
done

echo;
echo "Done"
echo;
echo `date`;

####################################################################################
