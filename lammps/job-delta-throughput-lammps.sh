#!/bin/bash
# Copyright (c) 2021-2022 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

#SBATCH --job-name=throughput-lammps
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --partition=cpu-interactive
#SBATCH --mem-per-cpu=4000m
#SBATCH --time=1:00:00
#SBATCH --account=bbgw-delta-cpu

cd /scratch/bbgw/joshuaan/hoomd-benchmarks/lammps

python -u benchmark_throughput.py --suffix lammps-epyc-7763

