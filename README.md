# HOOMD-blue benchmarks

This repository contains performance benchmarks for [HOOMD-blue][hoomd]. Use the benchmarks to test
your HOOMD-blue installation, check the performance of simulations on your hardware, or compare
simulation performance between different versions, build configurations, or systems.

## Requirements

* HOOMD-blue >=3.0
* numpy
* pandas

## Usage

1. Clone this repository:
  * `git clone --branch trunk --depth 1 https://github.com/glotzerlab/hoomd-benchmarks.git`
  * `cd hoomd-benchmarks`
2. Run a specific benchmark with options:
  * `python3 -m hoomd_benchmarks.md_pair_lj --device GPU`
  * `mpirun -n 2 python3 -m hoomd_benchmarks.md_pair_wca --device GPU -N 1000000 -v`
  * `mpirun -n 4 python3 -m hoomd_benchmarks.hpmc_sphere --device CPU -N 4000 --repeat 10`
3. Run the full benchmarks suite:
  * `python3 -m hoomd_benchmarks --device CPU`
  * `mpirun -n 8 python3 -m hoomd_benchmarks --device CPU`

The first execution will take some time as the benchmark generates the requested input
configuration. Subsequent runs with the same paramters will read input configurations from
`initial_configuration_cache/` if it exists. Activate the verbose `-v` command line option to see
status messages during the initial configuration generation and the benchmark execution.

## Scripting

Without the verbose flag, each benchmark module writes only a single performance number to stdout.
Use this in conjunction with scripts to execute a number of benchmarks and compare the results.
Python scripts can import the `hoomd_benchmarks` module and call the `Benchmark` classes directly.
See their docstrings for details.

## Common options

The following command line options are available for both the full test suite and individual
tests:

* `--device`: Set what device to execute the benchmark on. Either `CPU` or `GPU`.
* `-N`: Number of particles.
* `--rho`: Number density.
* `--dimensions`: Number of dimensions. Either `2` or `3`.
* `--warmup_steps`: Number of timesteps to run before timing.
* `--benchmark_steps`: Number of timesteps to run in the benchmark.
* `--repeat`: Number of times to repeat the run.
* `--verbose`: Enable verbose output.

When using the Python API, pass these options to the benchmark's constructor.

When running the full benchmark suite, `benchmark_steps` and `warmup_steps` set the number of steps
for **typical** benchmarks. Some unusually fast or slow benchmarks may scale the given value to
a larger or smaller number of actual steps.

When running individual benchmarks, `benchmark_steps`, and `warmup_steps` set the exact number of
steps to run with no scaling.

## The benchmark suite

Run the full suite with `python3 -m hoomd_benchmarks <options>`.

The full suite accepts the following command line options in addition to the common options:

* `--benchmarks`: Select the benchmarks to run by class name using `fnmatch` syntax.
* `--output`: Add column of benchmark results to or create the output CSV file.
* `--name`: Name identifying this benchmark run (leave unset to use the HOOMD-blue version).

## Benchmarks

Run any benchmark individually with `python3 -m hoomd_benchmarks.<benchmark_name> <options>`.
Some benchmarks have additional command line options, find these with
`python3 -m hoomd_benchmarks.<benchmark_name> --help`.

### Simulation benchmarks

Simulation benchmarks execute simulation runs with models representative of research use-cases and
report performance in time steps per second (MD) and trial moves per second per particle (HPMC).

* `hpmc_sphere` - Hard particle Monte Carlo simulation of spheres (diameter=1.0, d=0.1).
* `md_pair_lj` - Molecular dynamics simulation with the Lennard-Jones pair potential with the NVT
  integration method (epsilon=1, sigma=1, r_cut=2.5, kT=1.2, tau=0.5).
* `md_pair_opp` - Molecular dynamics simulation with theOPP pair potential with the NVT
  integration method (C1=1.7925807855607998, C2=1.7925807855607998, eta1=15, eta2=3, k=7.0,
  phi=5.5, r_cut=2.557, kT=1.2, tau=0.5).
* `md_pair_table` - Molecular dynamics simulation with the Lennard-Jones pair potential with the NVT
  integration method (epsilon=1, sigma=1, r_cut=2.5, kT=1.2, tau=0.5) - evaluated using
  ``hoomd.md.pair.Table``.
* `md_pair_wca` - Molecular dynamics simulation with the WCA pair potential with the NVT
  integration method (epsilon=1, sigma=1, r_cut=2**(1/6), kT=1.2, tau=0.5).

### Microbenchmarks

Microbenchmarks exercise a portion of the code and report performance with a metric specific to each
microbenchmark.

* `microbenchmark_box_reisze` - Measure the time steps per second of a sim with only box resize.
* `microbenchmark_empty_simulation` - Measure the time per step with an empty Simulation object.
* `microbenchmark_custom_trigger` - Measure the time taken per step to evaluate a custom trigger.
* `microbenchmark_custom_updater` - Measure the time taken per step to call a custom updater.
* `microbenchmark_custom_force` - Measure the time taken per step to use a constant custom force.
* `microbenchmark_get_snapshot` - Measure the time taken to call State.get_snapshot.
* `microbenchmark_set_snapshot` - Measure the time taken to call State.set_snapshot.
* `write_gsd` - Measure how many GSD frames (containing particle positions) can be written per
  second.
* `write_gsd_log` - Measure how many GSD frames (containing 1 logged value) can be written per
  second.
* `write_hdf5_log` - Measure how many HDF5 frames (containing 1 logged value) can be written per
  second.

## Change log

`hoomd_benchmarks` does not have a formal release cycle. Examine the git commit history to see the
changes.

## Contributing to HOOMD-blue

Contributions are welcome via [pull requests][pulls]. Please report bugs and suggest feature
enhancements via the [issue tracker][issues]. See [CONTRIBUTING.md](CONTRIBUTING.md) and
[ARCHITECTURE.md](ARCHITECTURE.md) for more information.

## Checking for performance regressions

To check for performance regressions before each HOOMD-relase:

1. Build the release candidate in `$HOME/build/hoomd/releases/<release>`
2. Run `job-gl-cpu.sh` and `job-gl-gpu.sh` on Great Lakes.
3. Run `python report.py` to generate the report.

## License

**HOOMD-blue** is available under the [3-clause BSD license](LICENSE).

[pulls]: https://github.com/glotzerlab/hoomd-benchmarks/pulls
[issues]: https://github.com/glotzerlab/hoomd-benchmarks/issues
[hoomd]: http://glotzerlab.engin.umich.edu/hoomd-blue/
