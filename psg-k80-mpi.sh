#!/bin/bash
#SBATCH --job-name="hoomd-k80-mpi"
#SBATCH --partition=hsw_k80
#SBATCH --ntasks-per-node=8
#SBATCH --nodes=8
#SBATCH --qos=big
#SBATCH -t 02:00:00

source $HOME/software/env.sh

export BENCHMARKS="hexagon microsphere"
./run-all.sh "psg" "k80-$$-4" "mpirun -n 4 python" "--mode=gpu" "0"
./run-all.sh "psg" "k80-$$-16" "mpirun -n 16 python" "--mode=gpu" "0"
./run-all.sh "psg" "k80-$$-64" "mpirun -n 64 python" "--mode=gpu" "0"
