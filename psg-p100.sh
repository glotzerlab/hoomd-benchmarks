#!/bin/bash
#SBATCH --job-name="hoomd-p100"
#SBATCH --partition=hsw_p100
#SBATCH --nodes=1
#SBATCH -t 02:00:00

source $HOME/software/env.sh

./run-all.sh "psg" "p100-$$" "mpirun -n 1 python" "--mode=gpu" "0"
