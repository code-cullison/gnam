#!/bin/bash

echo;
echo;


PROJ_DIR="/scratch/seismology/tcullison/test_mesh/Project_Beta_3E";
N_EVENTS=`\ls -ldtr $PROJ_DIR/run[0-9]* | wc -l`;
echo "Number of events to sum NORMS from: $N_EVENTS";
echo;

N_LOGS=`\ls -lrt ../logs/2_create_adj_srcs_run000*.out | wc -l`;
echo "Number of log files: $N_LOGS";
echo;

MYREM=`echo "scale=0; $N_LOGS%$N_EVENTS" | bc`
if [ $MYREM != 0 ]; then
  echo "!!!! ERROR !!!!";
  echo "There is a missmatchthe between the number of log files and the number of events.";
  echo;
  exit 0;
fi

N_ITER=`echo "scale=0; $N_LOGS/$N_EVENTS" | bc`

declare -A norms_array

for i in $(seq 1 $N_ITER); do 
  N_HEAD=`echo "scale=0; $i*$N_EVENTS" | bc`;
  ADJ_LOGS=`\ls -lrt ../logs/2_create_adj_srcs_run000*.out | head -$N_HEAD | tail -3 | rev | cut -d ' ' -f1 | rev`;
  echo "-------------------------------------------------------------------------------";
  echo " Iteration $i:";
  echo;
  echo " Adjoint files to parse for objective function norm:";
  echo "$ADJ_LOGS";
  echo;
  ITER_NORM=`grep -e 'norm' $ADJ_LOGS | tr -s ' ' | cut -d ' ' -f10 | awk '{s+=$1}END{print s}'`;
  echo " Total **-NORM-** (diff squared) for this iteration:";
  echo " $ITER_NORM";
  echo;
  norms_array+=([$i]=$ITER_NORM)
done
echo;


echo "-------------------------------------------------------------------------------";
echo " All **-NORMS-** (diff squared) in order:";
echo;

#for j in ${norms_array[@]}; do
for i in $(seq 1 $N_ITER); do 
  #echo " $j";
  echo " ${norms_array[$i]}";
done
echo;

