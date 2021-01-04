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

#set local project dir names
export EVENT_DIR="${SPEC_PROJ_DIR}/$1"


####################################################################################

echo;
echo "Creating adjsrc files for $1";
echo;
echo "cd $EVENT_DIR;"
cd $EVENT_DIR;
echo;

XPROG=bin/xcreate_adjsrc_waveform
#IFILE=0
IFILE=3 #HOPEFULY creates zeros for X and Y comps
WIN_DIR=OBS
OBS_DIR=FILT_OBS
SYN_DIR=FILT_SYN

for f in $WIN_DIR/NL.G*.window; do  
    STATION=$(echo ${f} | cut -d '/' -f2 | cut -d '.' -f1,2)
    WINFILE=$WIN_DIR/${STATION}.window
    LINE=$(sed -n '1p' < ${WINFILE})
    T0=$(echo $LINE | cut -d ' ' -f3)
    LINE=$(sed -n '2p' < ${WINFILE})
    T1=$(echo $LINE | cut -d ' ' -f3)
    #echo "T0,T1 = $T0,$T1"
    F_EAST_X=$SYN_DIR/${STATION}.FXX.semd 
    F_NORTH_Y=$SYN_DIR/${STATION}.FXY.semd 
    F_Z=$SYN_DIR/${STATION}.FXZ.semd 
    #echo "$XPROG $T0 $T1 $IFILE $F_EAST_X $F_NORTH_Y $F_Z $OBS_DIR";
    #$XPROG $T0 $T1 $IFILE $F_EAST_X $F_NORTH_Y $F_Z $OBS_DIR;
    echo "$XPROG $T0 $T1 $IFILE $F_Z $OBS_DIR";
    $XPROG $T0 $T1 $IFILE $F_Z $OBS_DIR;
done

# checks exit code
if [[ $? -ne 0 ]]; then 
  echo;
  echo "There was an error createing adjoint source files";
  exit 1; 
else
  echo;
  echo "Creating adjoint source fiels completed successfully";
fi


####################################################################################

#Move adjsrc files to the SEM directory
echo "mv $SYN_DIR/*.adj SEM";
mv $SYN_DIR/*.adj SEM;

echo;
echo "Done..."
echo "See results in directory: $EVENT_DIR/SEM"
echo;
echo `date`;
