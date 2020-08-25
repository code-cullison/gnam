#!/bin/bash
squeue -u $USER | tail -n+2 | awk -F' ' '{print $1}' | xargs -t -P0 -I {} scancel {};
