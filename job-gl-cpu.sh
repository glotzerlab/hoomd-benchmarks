#!/bin/bash
# Copyright (c) 2021-2022 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

#SBATCH --job-name=hoomd-benchmarks-cpu
#SBATCH --cpus-per-task=1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=36
#SBATCH --mem-per-cpu=4000m
#SBATCH --time=6:00:00
#SBATCH --account=sglotzer9
#SBATCH --partition=standard

cd $HOME/devel/hoomd-benchmarks
source $HOME/hoomd-dev-env.sh

rm cpu.csv

for version in `ls $HOME/build/hoomd-releases`; do
    export PYTHONPATH=$HOME/build/hoomd-releases/${version}
    mpirun -n 36 python3 -u -m hoomd_benchmarks --device CPU --output cpu.csv --name "${version}" --repeat 40 -v
done
