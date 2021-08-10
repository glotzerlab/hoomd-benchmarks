# HOOMD-blue benchmarks

This repository contains performance benchmarks for [HOOMD-blue][hoomd]. Use the benchmarks to test
your HOOMD-blue installation, check the performance of simulations on your hardware, or compare
simulation performance between different versions, build configurations, or systems.

1. Clone this repository:
  * `git clone https://github.com/glotzerlab/hoomd-benchmarks.git`
2. Run a specific benchmark with options:
  * `python3 -m hoomd_benchmarks.pair_lj --device GPU`
  * `python3 -m hoomd_benchmarks.pair_lj --device GPU -N 1000000`
  * `mpirun -n 4 python3 -m hoomd_benchmarks.pair_lj --device CPU  -N 4000 -v --repeat 10`
3. See the available options:
  * `python3 -m hoomd_benchmarks.pair_lj --help`

The first execution will take some time as the benchmark generates the requested input
configuration. Subsequent runs with the same paramters will start up faster as the system
configuration will be read from `initial_configuration_cache/` if it exists. Activate the verbose
`-v` command line option to see status messages during the initial configuration generation and the
benchmark execution.

## Scripting

Without the verbose flag, each benchmark script writes only a single performance number to stdout.
Use this in conjunction with scripts (e.g. shell scripts) to execute a number of benchmarks and
compare the results. Python scripts can import the `benchmark` function from each benchmark script's
module. See the documentation of each `benchmark` function for details.

[hoomd]: http://glotzerlab.engin.umich.edu/hoomd-blue/
