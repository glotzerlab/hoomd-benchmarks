#!/bin/bash
#SBATCH --job-name="hoomd-k40"
#SBATCH --partition=hsw_k40
#SBATCH --nodes=1
#SBATCH -t 02:00:00

source $HOME/software/env.sh

./run-all.sh "psg" "k40-$$" "mpirun -n 1 python" "--mode=gpu" "0"

export BENCHMARKS="microsphere hexagon"

./run-all.sh "psg" "k40-$$-4" "mpirun -n 4 python" "--mode=gpu" "0"
