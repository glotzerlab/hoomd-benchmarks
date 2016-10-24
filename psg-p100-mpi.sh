#!/bin/bash
#SBATCH --job-name="hoomd-p100-mpi"
#SBATCH --partition=hsw_p100
#SBATCH --ntasks-per-node=4
#SBATCH --nodes=4
#SBATCH --qos=big
#SBATCH -t 02:00:00

source $HOME/software/env.sh

export BENCHMARKS="hexagon microsphere"
./run-all.sh "psg" "p100-$$-4" "mpirun -n 4 python" "--mode=gpu" "0"
./run-all.sh "psg" "p100-$$-16" "mpirun -n 16 python" "--mode=gpu" "0"
# ./run-all.sh "psg" "p100-$$-64" "mpirun -n 64 python" "--mode=gpu" "0"
