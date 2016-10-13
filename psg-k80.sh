#!/bin/bash
#SBATCH --job-name="hoomd-k80"
#SBATCH --partition=hsw_k80
#SBATCH --nodes=1
#SBATCH -t 02:00:00

source $HOME/software/env.sh

./run-all.sh "psg" "k80-$$" "mpirun -n 1 python" "--mode=gpu" "0"

export BENCHMARKS="microsphere hexagon"
./run-all.sh "psg" "k80-$$" "mpirun -n 8 python" "--mode=gpu" "0"
