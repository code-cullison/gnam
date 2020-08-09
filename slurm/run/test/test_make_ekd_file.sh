#!/bin/bash
echo "make event_kernel_dirs.txt";
cat > event_kernel_dirs.txt <<EOF
OUTPUT_FILES/DATABASES_MPI/
../run0002/OUTPUT_FILES/DATABASES_MPI/
../run0003/OUTPUT_FILES/DATABASES_MPI/
EOF
echo "cat event_kernel_dirs.txt";
cat event_kernel_dirs.txt;
