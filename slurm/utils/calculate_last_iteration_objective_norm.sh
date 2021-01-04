#!/bin/bash

echo;
echo;

PROJ_DIR="/scratch/seismology/tcullison/test_mesh/Project_Beta_3E";
N_EVENTS=`\ls -ldtr $PROJ_DIR/run[0-9]* | wc -l`;
echo "Number of events to sum NORMS from: $N_EVENTS";
echo;

ADJ_LOGS=`\ls -lrt ../logs/2_create_adj_srcs_run000*.out | tail -3 | rev | cut -d ' ' -f1 | rev`;
echo "Adjoint files to parse for objective function norm:";
echo "$ADJ_LOGS";
echo;

ITER_NORM=`grep -e 'norm' $ADJ_LOGS | tr -s ' ' | cut -d ' ' -f10 | awk '{s+=$1}END{print s}'`;
echo "Total **-NORM-** (diff squared) for this iteration:";
echo "$ITER_NORM";
echo;
