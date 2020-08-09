#!/bin/bash

echo "source ./set_base_project_env.sh" > $RLOG;
source ../env/set_base_project_env.sh;

declare -A jobid_array
jid=0
for dir in ${SPEC_PROJ_DIR}/run[0-9][0-9][0-9][0-9]/; do
  RDIR=`echo "$dir" | rev | cut -d '/' -f2 | rev`;
  jobid_array+=([$RDIR]=$jid)
  ((jid=jid+1))
  echo "jobid_array[$RDIR] = ${jobid_array[$RDIR]}";
done
echo echo "full array: ${jobid_array[@]}";
STR=${jobid_array[@]}
CONCAT=`echo ${STR// /:}`;
echo "Concat: $CONCAT";
