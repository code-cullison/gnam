#!/bin/bash
squeue -u $USER | tail -17 | awk -F' ' '{print $1}' | xargs -t -P0 -I {} scancel {};
