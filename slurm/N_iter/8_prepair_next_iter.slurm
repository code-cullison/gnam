#!/bin/bash

echo `date`;

echo;
echo "SLURM_JOB_ID=$SLURM_JOB_ID";
echo "squeue -j $SLURM_JOB_ID:";
echo "$(squeue -j ${SLURM_JOB_ID})";
echo;

echo "pwd";
echo `pwd`;
echo;

####################################################################################

#get project env and setup modules
echo "source ../env/set_base_project_env.sh";
source ../env/set_base_project_env.sh;
echo "source ../env/set_project_modules.sh";
source ../env/set_project_modules.sh;
echo "source ../env/set_project_mpirun.sh";
source ../env/set_project_mpirun.sh;

#set local project dir names
export EVENT_DIR="${SPEC_PROJ_DIR}/run0001"
export OF_DIR="${EVENT_DIR}/OUTPUT_FILES"
export DB_MPI_DIR="${OF_DIR}/DATABASES_MPI"
export DATA_DIR="${EVENT_DIR}/DATA"
export OMOD_DIR="${EVENT_DIR}/OUTPUT_MODEL"
export SMOOTH_DIR="${EVENT_DIR}/SMOOTH"

#get current iteration number
echo;
echo "source $EVENT_DIR/current_iteration.sh";
source $EVENT_DIR/current_iteration.sh;
echo "Current Iteration: $CUR_ITER_NUM";
echo;


####################################################################################

echo;
echo;
echo "Renaming SYN DATA";
echo;
echo;
for dir in ${SPEC_PROJ_DIR}/run[0-9][0-9][0-9][0-9]/; do
  SDIR="${dir}/SYN"
  DATA_CMD="ls $SDIR/*.semd" 
  XARG_CMD="xargs -t -P0 -I {} mv ${SDIR}/{} ${SDIR}/{}.iter_${CUR_ITER_NUM}"
  echo "${DATA_CMD} | ${XARG_CMD}";
  echo `${DATA_CMD} | ${XARG_CMD}`;
done
echo;
echo;
echo "Renaming raw kernels";
echo;
echo;
for dir in ${SPEC_PROJ_DIR}/run[0-9][0-9][0-9][0-9]/; do
  KDIR="${dir}/OUTPUT_FILES/DATABASES_MPI"
  ALPH_CMD="ls $KDIR/proc*_alpha_kernel.bin" 
  BETA_CMD="ls $KDIR/proc*_beta_kernel.bin" 
  RHO_CMD="ls $KDIR/proc*_rho_kernel.bin" 
  HESS_CMD="ls $KDIR/proc*_hess_kernel.bin" 
  XARG_CMD="xargs -t -P0 -I {} mv ${KDIR}/{}.bin ${KDIR}/{}_iter_${CUR_ITER_NUM}.bin"
  echo "${ALPH_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}";
  echo `${ALPH_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}`;
  #echo "${BETA_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}";
  #echo `${BETA_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}`;
  #echo "${RHO_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}";
  #echo `${RHO_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}`;
  #echo "${HESS_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}";
  #echo `${HESS_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}`;
done
echo;
echo;
echo "Renaming SMOOTHED kernels";
echo;
echo;
ALPH_CMD="ls $SMOOTH_DIR/proc*_alpha_kernel_smooth.bin" 
BETA_CMD="ls $SMOOTH_DIR/proc*_beta_kernel_smooth.bin" 
RHO_CMD="ls $SMOOTH_DIR/proc*_rho_kernel_smooth.bin" 
HESS_CMD="ls $SMOOTH_DIR/proc*_hess_kernel_smooth.bin" 
XARG_CMD="xargs -t -P0 -I {} mv ${SMOOTH_DIR}/{}.bin ${SMOOTH_DIR}/{}_iter_${CUR_ITER_NUM}.bin"
echo "${ALPH_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}";
echo `${ALPH_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}`;
#echo "${BETA_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}";
#echo `${BETA_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}`;
#echo "${RHO_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}";
#echo `${RHO_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}`;
#echo "${HESS_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}";
#echo `${HESS_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}`;
echo;
echo;
echo "Renaming model model binaries";
echo;
echo;
VP_CMD="ls $DB_MPI_DIR/proc*_vp.bin"
VS_CMD="ls $DB_MPI_DIR/proc*_vs.bin"
RH_CMD="ls $DB_MPI_DIR/proc*_rho.bin"
XARG_CMD="xargs -t -P0 -I {} mv $DB_MPI_DIR/{}.bin $DB_MPI_DIR/{}_iter_${CUR_ITER_NUM}.bin"
echo "${VP_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}";
echo `${VP_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}`;
#echo "${VS_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}";
#echo `${VS_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}`;
#echo "${RH_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}";
#echo `${RH_CMD} | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | ${XARG_CMD}`;
echo;
echo;
echo "Copying update model model binaries";
echo;
echo;
for dir in ${SPEC_PROJ_DIR}/run[0-9][0-9][0-9][0-9]/; do
  E_DB_MPI_DIR="${dir}/OUTPUT_FILES/DATABASES_MPI"
  echo "Copy updated model binaries to $E_DB_MPI_DIR" 
  VP_CMD="ls $OMOD_DIR/proc*_vp_new.bin"
  VS_CMD="ls $OMOD_DIR/proc*_vs_new.bin"
  RH_CMD="ls $OMOD_DIR/proc*_rho_new.bin"
  XARG_CMD="xargs -t -P0 -I {} cp $OMOD_DIR/{}_new.bin $E_DB_MPI_DIR/{}.bin"
  echo "${VP_CMD} | rev | cut -d '/' -f1 | rev | cut -d '_' -f1,2 | ${XARG_CMD}";
  echo `${VP_CMD} | rev | cut -d '/' -f1 | rev | cut -d '_' -f1,2 | ${XARG_CMD}`;
  #echo "${VS_CMD} | rev | cut -d '/' -f1 | rev | cut -d '_' -f1,2 | ${XARG_CMD}";
  #echo `${VS_CMD} | rev | cut -d '/' -f1 | rev | cut -d '_' -f1,2 | ${XARG_CMD}`;
  #echo "${RH_CMD} | rev | cut -d '/' -f1 | rev | cut -d '_' -f1,2 | ${XARG_CMD}";
  #echo `${RH_CMD} | rev | cut -d '/' -f1 | rev | cut -d '_' -f1,2 | ${XARG_CMD}`;
done
echo;
echo;
NEW_ITER_NUM=$((CUR_ITER_NUM+=1))
echo "Changing Old Iteration $CUR_ITER_NUM to New Iteration $NEW_ITER_NUM";
echo;
echo "echo #!/bin/bash > $EVENT_DIR/current_iteration.sh";
echo "#!/bin/bash" > $EVENT_DIR/current_iteration.sh;
echo "echo CUR_ITER_NUM=$NEW_ITER_NUM >> $EVENT_DIR/current_iteration.sh";
echo "CUR_ITER_NUM=$NEW_ITER_NUM" >> $EVENT_DIR/current_iteration.sh;
echo;
echo;
echo "Done..."
echo "See results in directory: $SPEC_PROJ_DIR"
echo `date`
