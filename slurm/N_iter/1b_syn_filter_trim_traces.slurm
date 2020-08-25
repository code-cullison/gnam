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

####################################################################################

echo "cd $SPEC_PROJ_DIR;"
cd $SPEC_PROJ_DIR;
echo "pwd"'
echo `pwd`'
echo "ls pyutils/rwftr.py";
ls pyutils/rwftr.py;

##*****************************************##

echo;
echo "Filtering and Trimming Synthetic Traces";
echo;

T0="0.0"
TN="16.383"
F1="2.0"
F2="6.0"
SR="1000"
IDIR=SYN
ODIR=FILT_SYN
XPROG="pyutils/rwftr.py --t0=${T0} --tN=${TN} --f1=${F1} --f2=${F2} --sr=${SR}"

echo "\\ls -d run[0-9]* | xargs -t -P0 -I {} ${XPROG} --idir={}/$IDIR --odir={}/$ODIR";
\ls -d run[0-9]* | xargs -t -P0 -I {} ${XPROG} --idir={}/$IDIR --odir={}/$ODIR;


# checks exit code
if [[ $? -ne 0 ]]; then 
  echo;
  echo "There was an error createing adjoint source files";
  exit 1; 
else
  echo;
  echo "Creating adjoint source fiels completed successfully";
fi

##*****************************************##


echo
echo "Done..."
echo "See results in directory: ${SPEC_PROJ_DIR}/run####/$ODIR directories"
echo `date`
