#!/bin/bash
# Copyright (c) 2021-2022 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

#SBATCH --job-name=hoomd-benchmarks-gpu
#SBATCH --cpus-per-task=1
#SBATCH --nodes=1
#SBATCH --gpus=v100:1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=4000m
#SBATCH --time=60:00
#SBATCH --account=sglotzer9
#SBATCH --partition=gpu

cd $HOME/devel/hoomd-benchmarks
source $HOME/hoomd-dev-env.sh

rm gpu.csv

for version in `ls $HOME/build/hoomd-releases`; do
    export PYTHONPATH=$HOME/build/hoomd-releases/${version}
    mpirun -n 1 python3 -u -m hoomd_benchmarks --device GPU --output gpu.csv --name "${version}" --repeat 40 -v
done
