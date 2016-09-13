#!/bin/bash
#PBS -N hoomd-benchmarks
#PBS -l nodes=64,walltime=2:00:00
#PBS -A mat110
#PBS -j oe
#PBS -m abe

cd ${PBS_O_WORKDIR}

source /ccs/proj/mat110/software/joaander/titan-env1/env.sh

export BENCHMARKS="microsphere hexagon"
./run-all.sh "titan" "gpu64-$$" "aprun -n 64 -N 1 -b python" "--mode=gpu" "0"
