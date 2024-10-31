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

cd $HOME/devel/hoomd-benchmarks
module load openmpi/4.1.6 cuda/12.3.0

source /projects/bbgw/software/micromamba-configuration.sh
micromamba activate software
export LD_PRELOAD=$MAMBA_ROOT_PREFIX/envs/software/lib/libstdc++.so

version=$(python -c "import hoomd; print(hoomd.version.version)")
srun -n 1 python3 -u -m hoomd_benchmarks --device GPU --output gpu.csv --name "${version}" --repeat 20 -v
srun -n 16 python3 -u -m hoomd_benchmarks --device CPU --output cpu.csv --name "${version}" --repeat 10 -v
