#!/bin/bash

source /quanta1/home/tcullison/examples/specfem3D/test_create_mesh/scripts/env/proj_config.sh;

EVENT_DIR=${SPEC_PROJ_DIR}/run0001

CUR_ITER_FILE=$EVENT_DIR/current_iteration.sh
if [ -f "$CUR_ITER_FILE" ]; then
  echo "$CUR_ITER_FILE exists."
else 
  echo "$CUR_ITER_FILE does not exist."
fi
