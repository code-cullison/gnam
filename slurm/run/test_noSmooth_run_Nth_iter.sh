#!/bin/bash

THISNAME=`echo $0 | rev | cut -d '/' -f1 | cut -d '.' -f2 | rev | cut -d '_' -f2,3`;

###########################################
#
# Read arguments
#
###########################################


SPEC_ARCH="CPU"
SPEC_NPROC=1
SPEC_ITER=0
LOG_PATH="./"
NPU=""
PJID=""
CUR_ITER_NUM=0

for i in "$@"; do
  case $i in
    -nCPU=*)
    SPEC_NPROC="${i#*=}"
    NPU="-nCPU=$SPEC_NPROC"
    NCPU="SET"
    ;;
    -nGPU=*)
    SPEC_NPROC="${i#*=}"
    SPEC_ARCH="GPU"
    NPU="-nGPU=$SPEC_NPROC"
    NGPU="SET"
    ;;
    -lp=*)
    LOG_PATH="${i#*=}"
    ;;
    -w=*)
    PJID="${i#*=}"
    ;;
    *)
    echo "unknown option"
    exit 2;
    ;;
  esac
done

if [[ $NCPU == $NGPU ]]; then
  echo "-nCPU and -nGPU cannot both be set at the same time.";
  exit 2;
fi

LDATE=`date +.on.%F.at.%H:%M:%S`
RLOG="${LOG_PATH}${THISNAME}${LDATE}.rlog"

echo "source ../env/set_base_project_env.sh" >> $RLOG;
source ../env/set_base_project_env.sh;

BASE_EVENT_DIR=${SPEC_PROJ_DIR}/run0001
CUR_ITER_FILE=$BASE_EVENT_DIR/current_iteration.sh
if [ -f "$CUR_ITER_FILE" ]; then
  echo "source $CUR_ITER_FILE" >> $RLOG;
  echo "Current Iteration: $CUR_ITER_NUM" >> $RLOG;
  source $CUR_ITER_FILE;
else 
  echo "$CUR_ITER_FILE does not exist.";
  exit 2;
fi

###########################################
#
# Step-0: Forward Solver
#
###########################################

JNAME="fwd_solver";
PROG="../N_iter/0_fwd_solver_event.slurm";

if [[ ! -z $PJID ]]; then
  PJID="-w=afterok:$PJID";
fi

declare -A jobid_array
#jid=0
for dir in ${SPEC_PROJ_DIR}/run[0-9][0-9][0-9][0-9]/; do
  RDIR=`echo "$dir" | rev | cut -d '/' -f2 | rev` >> $RLOG
  OLOG="0_${JNAME}_$RDIR.job.%N.%j.out"  #STDOUT Log
  ELOG="0_${JNAME}_$RDIR.job.%N.%j.err"  #STDERR Log
  echo "CJID=\$(./spec_sbatch.sh $PJID -o=$OLOG -e=$ELOG $NPU -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa=$RDIR)" >> $RLOG;
  CJID=$(./spec_sbatch.sh $PJID -o=$OLOG -e=$ELOG $NPU -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa=$RDIR);
  echo "SLURM JOBID: $CJID" >> $RLOG;
  CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;
  #CJID=$jid
  jobid_array+=([$RDIR]=$CJID)
  #((jid=jid+1))
  echo "add job to jobid_array[$RDIR] = ${jobid_array[$RDIR]}" >> $RLOG;
  echo "full jobid array: ${jobid_array[@]}" >> $RLOG;
done
STR=${jobid_array[@]};
CJID=`echo ${STR// /:}`; #concatenated jobs with ':' for delimeters


##------- Set SAVE_MESH = .false. ---------------------##

if [[ $CUR_ITER_NUM == 0 ]]; then 
  CJID="afterok:$CJID";

  JNAME="save_mesh_eq_false";
  OLOG="parfile_0_${JNAME}.job.%N.%j.out";  # STDOUT
  ELOG="parfile_0_${JNAME}.job.%N.%j.err";  # STDERR
  PROG="../parfile/change_save_mesh.sh";

  #Note: that NPU is NOT passed as an argument
  echo "CJID=\$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa="false")" >> $RLOG;
  CJID=$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa="false");

  echo "SLURM JOBID: $CJID" >> $RLOG;
  CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;
fi

######################################################
#
# Step-1a: Filter OBSERVED DATA #FIXME:Alays filter?
#
######################################################
CJID="afterok:$CJID";
NJID=$CJID; #used for the next job

JNAME="obs_filter_trim";
OLOG="1a_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="1a_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../N_iter/1a_obs_filter_trim_traces.slurm";

#Note: that NPU is NOT passed as an argument
echo "CJID=\$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG)" >> $RLOG;
CJID=$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG);

echo "SLURM JOBID: $CJID" >> $RLOG;
CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;


###########################################
#
# Step-1b: Filter SYNTHETIC DATA
#
###########################################
SJID=$CJID;

JNAME="syn_filter_trim";
OLOG="1b_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="1b_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../N_iter/1b_syn_filter_trim_traces.slurm";

#Note: that NPU is NOT passed as an argument
#Note: that $NJID is used INSTEAD of $CJID
echo "CJID=\$(./spec_sbatch.sh -w=$NJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG)" >> $RLOG;
CJID=$(./spec_sbatch.sh -w=$NJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG);

echo "SLURM JOBID: $CJID" >> $RLOG;
CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;
CJID="$SJID:$CJID";

###########################################
#
# Step-2: Create adjoint sources
#
###########################################
CJID="afterok:$CJID";

JNAME="create_adj_srcs";
OLOG="2_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="2_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../N_iter/2_create_adj_srcs.slurm";

declare -A adj_jobid_array

for dir in ${SPEC_PROJ_DIR}/run[0-9][0-9][0-9][0-9]/; do
  RDIR=`echo "$dir" | rev | cut -d '/' -f2 | rev` >> $RLOG
  OLOG="2_${JNAME}_$RDIR.job.%N.%j.out"  #STDOUT Log
  ELOG="2_${JNAME}_$RDIR.job.%N.%j.err"  #STDERR Log
  echo "CJID=\$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa=$RDIR)" >> $RLOG;
  TJID=$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa=$RDIR);
  echo "SLURM JOBID: $TJID" >> $RLOG;
  TJID=`echo ${TJID} | rev | cut -d ' ' -f1 | rev`;
  adj_jobid_array+=([$RDIR]=$TJID)
done
STR=${adj_jobid_array[@]};
CJID=`echo ${STR// /:}`; #concatenated jobs with ':' for delimeters


###########################################
#
# Step-3: Adjoint Kernels
#
###########################################
CJID="afterok:$CJID";

JNAME="adj_kernels";
OLOG="3_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="3_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../N_iter/3_adj_kernels_event.slurm";

declare -A kernel_jobid_array

for dir in ${SPEC_PROJ_DIR}/run[0-9][0-9][0-9][0-9]/; do
  RDIR=`echo "$dir" | rev | cut -d '/' -f2 | rev` >> $RLOG
  OLOG="3_${JNAME}_$RDIR.job.%N.%j.out"  #STDOUT Log
  ELOG="3_${JNAME}_$RDIR.job.%N.%j.err"  #STDERR Log
  echo "CJID=\$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG $NPU -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa=$RDIR)" >> $RLOG;
  TJID=$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG $NPU -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa=$RDIR);
  echo "SLURM JOBID: $TJID" >> $RLOG;
  TJID=`echo ${TJID} | rev | cut -d ' ' -f1 | rev`;
  kernel_jobid_array+=([$RDIR]=$TJID)
done
STR=${kernel_jobid_array[@]};
CJID=`echo ${STR// /:}`; #concatenated jobs with ':' for delimeters


###########################################################
#
# Step-4: Combine event kernels (still separate domains
#
###########################################################
CJID="afterok:$CJID"; 

JNAME="combine_event_kernels";
OLOG="4_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="4_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../N_iter/4_combine_event_kernels.slurm";

echo "CJID=\$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG $NPU -lp=$LOG_PATH -jn=$JNAME -x=$PROG)" >> $RLOG;
CJID=$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG $NPU -lp=$LOG_PATH -jn=$JNAME -x=$PROG);

echo "SLURM JOBID: $CJID" >> $RLOG;
CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;


###########################################################
#
# Step-5a: Smooth Combined Kernels (alpha and beta)
#
###########################################################
CJID="afterok:$CJID"; 
NJID=$CJID; #used for the next job

JNAME="dummy_ab_kernels";
OLOG="5a_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="5a_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../N_iter/5a_dummy_smooth_ab_kernels.slurm";

echo "CJID=\$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG $NPU -lp=$LOG_PATH -jn=$JNAME -x=$PROG)" >> $RLOG;
CJID=$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG $NPU -lp=$LOG_PATH -jn=$JNAME -x=$PROG);

echo "SLURM JOBID: $CJID" >> $RLOG;
CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;


###########################################################
#
# Step-5b: Smooth Combined Kernels (rho and hess)
#
###########################################################
SJID=$CJID;

JNAME="dummy_rh_kernels";
OLOG="5b_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="5b_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../N_iter/5b_dummy_smooth_rh_kernels.slurm";

#Note: that $NJID is used INSTEAD of $CJID
echo "CJID=\$(./spec_sbatch.sh -w=$NJID -o=$OLOG -e=$ELOG $NPU -lp=$LOG_PATH -jn=$JNAME -x=$PROG)" >> $RLOG;
CJID=$(./spec_sbatch.sh -w=$NJID -o=$OLOG -e=$ELOG $NPU -lp=$LOG_PATH -jn=$JNAME -x=$PROG);

echo "SLURM JOBID: $CJID" >> $RLOG;
CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;
CJID="$SJID:$CJID";


###########################################################
#
# Step-6: Preconditon Combine event kernels 
#
###########################################################
CJID="afterok:$CJID"; 

JNAME="precond_combine_kernels";
OLOG="6_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="6_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../N_iter/6_precond_combine_kernels.slurm";

#Note: that $NJID is used INSTEAD of $CJID
echo "CJID=\$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG $NPU -lp=$LOG_PATH -jn=$JNAME -x=$PROG)" >> $RLOG;
CJID=$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG $NPU -lp=$LOG_PATH -jn=$JNAME -x=$PROG);

CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;


###########################################################
#
# Step-7: Update Model (still decomposed)
#
###########################################################
CJID="afterok:$CJID"; 

JNAME="model_update";
OLOG="7_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="7_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../N_iter/7_model_update.slurm";
STEP=0.10

echo "CJID=\$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG $NPU -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa=$STEP)" >> $RLOG;
CJID=$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG $NPU -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa=$STEP);

echo "SLURM JOBID: $CJID" >> $RLOG;
CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;


###########################################################
#
# Step-8: Prepare Next Iteration
#
###########################################################
CJID="afterok:$CJID"; 

JNAME="prepair_next_iter";
OLOG="8_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="8_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../N_iter/8_prepair_next_iter.slurm";

#Note: that NPU is NOT passed as an argument
echo "CJID=\$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG)" >> $RLOG;
CJID=$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG);

echo "SLURM JOBID: $CJID" >> $RLOG;
CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;


###########################################################
#
# Step-9: Run Generate Databases for updated model
#
###########################################################

##------- Set MODEL = gll ---------------------##

if [[ $CUR_ITER_NUM == 0 ]]; then 
  CJID="afterok:$CJID";

  JNAME="change_model_gll";
  OLOG="parfile_9_${JNAME}.job.%N.%j.out";  # STDOUT
  ELOG="parfile_9_${JNAME}.job.%N.%j.err";  # STDERR
  PROG="../parfile/change_model.sh";

  #Note: that NPU is NOT passed as an argument
  echo "CJID=\$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa="gll")" >> $RLOG;
  CJID=$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG -lp=$LOG_PATH -jn=$JNAME -x=$PROG -xa="gll");

  echo "SLURM JOBID: $CJID" >> $RLOG;
  CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;
fi

##------- Generate Databases ------------------##

CJID="afterok:$CJID";

JNAME="next_gen_db_mpi";
OLOG="9_${JNAME}.job.%N.%j.out";  # STDOUT
ELOG="9_${JNAME}.job.%N.%j.err";  # STDERR
PROG="../N_iter/9_generate_databases.slurm";

echo "CJID=\$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG $NPU -lp=$LOG_PATH -jn=$JNAME -x=$PROG)" >> $RLOG;
CJID=$(./spec_sbatch.sh -w=$CJID -o=$OLOG -e=$ELOG $NPU -lp=$LOG_PATH -jn=$JNAME -x=$PROG);

echo "SLURM JOBID: $CJID" >> $RLOG;
CJID=`echo ${CJID} | rev | cut -d ' ' -f1 | rev`;


################################################################
#
# Final-Step: echo SLURM Job ID's still to be waited on.
#
################################################################
echo $CJID
