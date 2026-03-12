#!/bin/bash
#SBATCH --job-name=hoomd-blue
#SBATCH --account=dmr140129
#SBATCH --partition=wholenode
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=2
#SBATCH --time=120

eval "$(pixi shell-hook --environment hoomd)"

srun -n 1 python -m hoomd_benchmarks.hoomd-rs-compare
srun -n 2 python -m hoomd_benchmarks.hoomd-rs-compare
srun -n 8 python -m hoomd_benchmarks.hoomd-rs-compare
srun -n 16 python -m hoomd_benchmarks.hoomd-rs-compare
srun -n 32 python -m hoomd_benchmarks.hoomd-rs-compare
srun -n 64 python -m hoomd_benchmarks.hoomd-rs-compare
