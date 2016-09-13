#!/bin/bash
#PBS -N hoomd-benchmarks
#PBS -l nodes=3:ppn=24,walltime=24:00:00
#PBS -l gres=cpuslots
#PBS -A sglotzer_fluxoe
#PBS -l qos=flux
#PBS -q fluxoe
#PBS -j oe
#PBS -m n

cd ${PBS_O_WORKDIR}

source $HOME/test-env3/env.sh

export BENCHMARKS="lj-liquid triblock-copolymer quasicrystal microsphere hexagon"
./run-all.sh "flux" "cpu72-$$" "mpirun python" "--mode=cpu" "0"

# depletion can run on 3x3x3 max, use 12 cores to get one full CPU
export BENCHMARKS="depletion"
./run-all.sh "flux" "cpu12-$$" "mpirun -n 12 python" "--mode=cpu" "0"
