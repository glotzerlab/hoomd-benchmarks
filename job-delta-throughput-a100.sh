#!/bin/bash
# Copyright (c) 2021-2022 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

#SBATCH --job-name=throughput-a100
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --gpus-per-node=1
#SBATCH --partition=gpuA100x4-interactive
#SBATCH --mem-per-cpu=8000m
#SBATCH --time=1:00:00
#SBATCH --account=bbgw-delta-gpu

cd /scratch/bbgw/joshuaan/hoomd-benchmarks

python -u benchmark_throughput.py --device GPU --suffix a100

