#!/bin/bash
# Copyright (c) 2021-2022 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

#SBATCH --job-name=hoomd-benchmarks
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --cpus-per-task=1
#SBATCH --gpus-per-node=1
#SBATCH --partition=gpuA100x4
#SBATCH --mem-per-cpu=4000m
#SBATCH --time=6:00:00
#SBATCH --account=bbgw-delta-gpu
#SBATCH --constraint="scratch"

export RELEASES_DIR=/scratch/bbgw/joshuaan/hoomd-releases

cd $HOME/devel/hoomd-benchmarks
source $HOME/hoomd-dev-env.sh

rm gpu.csv

for version in $(ls ${RELEASES_DIR})
do
    export PYTHONPATH=${RELEASES_DIR}/${version}
    srun -n 1 python3 -u -m hoomd_benchmarks --device GPU --output gpu.csv --name "${version}" --repeat 20 -v
done

rm cpu.csv

for version in $(ls ${RELEASES_DIR})
do
    export PYTHONPATH=${RELEASES_DIR}/${version}
    srun -n 16 python3 -u -m hoomd_benchmarks --device CPU --output cpu.csv --name "${version}" --repeat 10 -v
done
