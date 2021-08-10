# HOOMD-blue benchmarks

This repository contains performance benchmarks for [HOOMD-blue][hoomd]. Use the benchmarks to test
your HOOMD-blue installation, check the performance of simulations on your hardware, or compare
simulation performance between different versions, build configurations, or systems.

## Usage

1. Clone this repository:
  * `git clone https://github.com/glotzerlab/hoomd-benchmarks.git`
  * `cd hoomd-benchmarks`
2. Run a specific benchmark with options:
  * `python3 -m hoomd_benchmarks.md_pair_lj --device GPU`
  * `mpirun -n 2 python3 -m hoomd_benchmarks.md_pair_wca --device GPU -N 1000000 -v`
  * `mpirun -n 4 python3 -m hoomd_benchmarks.hpmc_sphere --device CPU -N 4000 --repeat 10`
3. Run the full benchmarks suite:
  * `mpirun -n 8 python3 -m hoomd_benchmarks --device CPU`
4. See the available command line options:
  * `python3 -m hoomd_benchmarks.md_pair_lj --help`

The first execution will take some time as the benchmark generates the requested input
configuration. Subsequent runs with the same paramters will start up faster as the system
configuration will be read from `initial_configuration_cache/` if it exists. Activate the verbose
`-v` command line option to see status messages during the initial configuration generation and the
benchmark execution.

## Scripting

Without the verbose flag, each benchmark module writes only a single performance number to stdout.
Use this in conjunction with scripts to execute a number of benchmarks and compare the results.
Python scripts can import the `hoomd_benchmarks` module and call the `Benchmark` classes directly.
See their docstrings for details.

## Benchmarks

Run any of these benchmarks individually with: `python3 -m hoomd_benchmarks.<benchmark_name>`:

* `hpmc_sphere` - Hard particle Monte Carlo simulation of spheres (diameter=1.0, d=0.1)
* `md_pair_lj` - Molecular dynamics simulation with the Lennard-Jones pair potential with the NVT
  integration method (epsilon=1, sigma=1, r_cut=2.5, kT=1.2, tau=0.5).
* `md_pair_wca` - Molecular dynamics simulation with the WCA pair potential with the NVT
  integration method (epsilon=1, sigma=1, r_cut=2**(1/6), kT=1.2, tau=0.5).

## Change log

`hoomd_benchmarks` does not have a formal release cycle. Examine the git commit history to see the
changes.

## Contributing to HOOMD-blue

Contributions are welcome via [pull requests][pulls]. Please report bugs and suggest feature
enhancements via the [issue tracker][issues]. See [CONTRIBUTING.md](CONTRIBUTING.md) and
[ARCHITECTURE.md](ARCHITECTURE.md) for more information.

## License

**HOOMD-blue** is available under the [3-clause BSD license](LICENSE).

[pulls]: https://github.com/glotzerlab/hoomd-benchmarks/pulls
[issues]: https://github.com/glotzerlab/hoomd-benchmarks/issues
[hoomd]: http://glotzerlab.engin.umich.edu/hoomd-blue/
