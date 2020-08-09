#!/bin/bash

echo;
echo "Setup Project Directoies";
echo;


source ../env/proj_config.sh;


# Make Project Root Directory
echo;
echo "**  Make Project Root Directory  **"
echo;
echo "mkdir $SPEC_PROJ_DIR";
mkdir $SPEC_PROJ_DIR;
echo;


# Make Mesh Directory
echo;
echo "**  Make Mesh Directory  **"
echo;
echo "mkdir $MESH_DIR";
mkdir $MESH_DIR;
echo;


# Make pyutils and bash script links
echo;
echo "**  Make pyutils and script links  **";
echo;
echo "ln -s $SPEC_PYUTILS $SPEC_PROJ_DIR/pyutils";
ln -s $SPEC_PYUTILS $SPEC_PROJ_DIR/pyutils;
echo;
echo "ln -s $SPEC_SCRPUTL $SPEC_PROJ_DIR/scriptutils";
ln -s $SPEC_SCRPUTL $SPEC_PROJ_DIR/scriptutils;
echo;


# Make Event Directories
echo;
echo "**  Make Event Directories  **";
echo;
ZEROS='0000'
NDIGI=${#ZEROS}
for (( i = 1; i <= $SPEC_N_EVENTS; i += 1 )) do  
  ICUT=`expr $NDIGI - ${#i}` 
  POST_FIX="${ZEROS:0:${ICUT}}${i}"
  echo "mkdir ${SPEC_PROJ_DIR}/run${POST_FIX}";
  mkdir "${SPEC_PROJ_DIR}/run${POST_FIX}";
done


# Make Event Sub Directories and links
echo;
echo "**  Make Event Sub Directories and links  **";
echo;
for dir in ${SPEC_PROJ_DIR}/run[0-9][0-9][0-9][0-9]/; do
  mkdir $dir/DATA $dir/OUTPUT_FILES;
  echo "mkdir $dir/DATA $dir/OUTPUT_FILES";
  mkdir $dir/OUTPUT_FILES/DATABASES_MPI;
  echo "mkdir $dir/OUTPUT_FILES/DATABASES_MPI";
  mkdir $dir/OBS $dir/SYN $dir/SEM;
  echo "mkdir $dir/OBS $dir/SYN $dir/SEM";
  mkdir $dir/FILT_OBS $dir/FILT_SYN;
  echo "mkdir $dir/FILT_OBS $dir/FILT_SYN";
  ln -s $SPEC_GPU_BIN/bin $dir/bin;
  echo "ln -s $SPEC_GPU_BIN/bin $dir/bin";
  ln -s $SPEC_GPU_BIN/utils $dir/utils;
  echo "ln -s $SPEC_GPU_BIN/utils $dir/utils";
done


# Make Base Event Directories, links, and special files
echo;
echo "**  Make Base Event Directories  **";
echo;
BE_DIR="$SPEC_PROJ_DIR/run0001"

echo "mkdir $BE_DIR/INPUT_GRADIENT $BE_DIR/INPUT_KERNELS $BE_DIR/INPUT_MODEL";
mkdir $BE_DIR/INPUT_GRADIENT $BE_DIR/INPUT_KERNELS $BE_DIR/INPUT_MODEL;
echo "mkdir $BE_DIR/OUTPUT_MODEL $BE_DIR/OUTPUT_SUM";
mkdir $BE_DIR/OUTPUT_MODEL $BE_DIR/OUTPUT_SUM;
echo "mkdir $BE_DIR/COMBINE $BE_DIR/SMOOTH $BE_DIR/topo";
mkdir $BE_DIR/COMBINE $BE_DIR/SMOOTH $BE_DIR/topo;


echo;
echo "**  Make Base Event links, and special files **";
echo;
echo "echo $BE_DIR/OUTPUT_FILES/DATABASES_MPI > $BE_DIR/event_kernel_dirs.txt";
echo "$BE_DIR/OUTPUT_FILES/DATABASES_MPI" > $BE_DIR/event_kernel_dirs.txt;
for dir in ${SPEC_PROJ_DIR}/run[0-9][0-9][0-9][0-9]/; do
  RDIR=`echo "$dir" | rev | cut -d '/' -f2 | rev`;
  if [[ $RDIR == "run0001" ]]; then
    continue;
  fi
  echo "echo $dir/OUTPUT_FILES/DATABASES_MPI >> $BE_DIR/event_kernel_dirs.txt";
  echo "$dir/OUTPUT_FILES/DATABASES_MPI" >> $BE_DIR/event_kernel_dirs.txt;
done

echo "ln -s $BE_DIR/SMOOTH $BE_DIR/INPUT_KERNELS/event0001";
ln -s $BE_DIR/SMOOTH $BE_DIR/INPUT_KERNELS/event0001 
echo "echo event0001 > $BE_DIR/kernels_list.txt";
echo "event0001" > $BE_DIR/kernels_list.txt
