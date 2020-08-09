#!/bin/bash
source ../env/set_base_project_env.sh;
EVENT_DIR="${SPEC_PROJ_DIR}/run0001"
source $EVENT_DIR/current_iteration.sh;
echo "Current iteration: $CUR_ITER_NUM"
NEW_ITER_NUM=$((CUR_ITER_NUM+=1))
echo "Next iteration: $NEW_ITER_NUM"
