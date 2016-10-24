#!/bin/bash
#SBATCH --job-name="hoomd-k40-mpi"
#SBATCH --partition=hsw_k40
#SBATCH --ntasks-per-node=4
#SBATCH --nodes=1
#SBATCH -t 02:00:00

source $HOME/software/env.sh

export BENCHMARKS="hexagon microsphere"
./run-all.sh "psg" "k40-$$-4" "mpirun -n 4 python" "--mode=gpu" "0"
# ./run-all.sh "psg" "k40-$$-16" "mpirun -n 16 python" "--mode=gpu" "0"
# ./run-all.sh "psg" "k40-$$-64" "mpirun -n 64 python" "--mode=gpu" "0"
