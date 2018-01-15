#!/bin/bash

#SBATCH --job-name="hoomd-p100-mpi"
#SBATCH --partition=gpu
#SBATCH --gres=gpu:p100:4
#SBATCH --ntasks-per-node=28
#SBATCH --nodes=4
#SBATCH -t 02:00:00

source $HOME/test-env-gpu/env.sh

export BENCHMARKS="hexagon microsphere"
./run-all.sh "comet" "p100-$$-4" "mpirun -n 4 python" "--mode=gpu" "0"
./run-all.sh "comet" "p100-$$-16" "mpirun -n 16 python" "--mode=gpu" "0"
# ./run-all.sh "comet" "p100-$$-64" "mpirun -n 64 python" "--mode=gpu" "0"
