#!/bin/bash

#SBATCH --job-name="hoomd-p100"
#SBATCH --partition=gpu-shared
#SBATCH --gres=gpu:p100:1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=7
#SBATCH --no-requeue
#SBATCH -t 02:00:00

source $HOME/test-env-gpu/env.sh

./run-all.sh "comet" "p100-$$" "mpirun -n 1 python" "--mode=gpu" "0"
