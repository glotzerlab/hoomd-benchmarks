# Architecture

## Design goals

The code in this repository is designed to execute simulations with HOOMD-blue and measure their
performance. Users of this code should be able to:

1. Execute a variety of benchmarks individually or in groups. The benchmarks cover test cases
   ranging from microbenchmarks of specific potentials to research-relevant simulations that measure
   I/O, analysis, and other overheads.
2. Choose parameters for the benchmark such as the number of particles, the density, r_cut, and
   others.
3. Run benchmarks on the CPU, GPU, multiple CPUs, or multiple GPUs.
4. Use profiling tools with the benchmarks to obtain details on the execution.
5. Compare performance between runs on different hardware and/or different versions of HOOMD-blue.

## Implementation

To meet these design goals, each benchmark is implemented in a separate Python script that accepts
parameters and device options as command line arguments. Each script writes a single number to
standard out indicating the performance of the run, unless the verbose flag is given which prints
additional details. This allows users to run single benchmarks with varying parameters manually from
the command line (to meet goals 2,3, and especially 4) or automatically from shell scripts, Python
scripts, or other systems to meet goal 5.

The code is organized in the `hoomd_benchmarks` package so that benchmark scripts can share common
code, such as initialization and command line option parsing. Individual benchmarks implement a
`main` method that can be called by Python scripts and a `if __name__ == '__main__'` section to
execute the benchmark with `python3 -m hoomd_benchmarks.benchmark_name`.

To meet goal 5, `hoomd_benchmarks` defines a suite of tests that runs each benchmark with default
parameters and provides a report. Users that wish to perform specific studies (such as system size
performance scaling) are welcome to implement their own protocols in their preferred language.

## Handling initialization

Before a benchmark can execute, it needs a suitable initial configuration. The script must generate
the initial configuration to match the parameters given the the user to meet goal 2. At the same
time, users will not want to wait to generate the initial configuration every time they run the
benchmark - especially when running repeated benchmarks, or running in a profiling tool that
instruments and slows execution. Users also find it inconvenient to run multiple scripts in stages
(init, then benchmark) unless those stages are managed by a workflow engine. Using a workflow engine
would overly complicate these benchmarks, especially for goals 3 and 4.

Taking all this into consideration, the benchmark scripts cache input files and do the following:

* Load the initial configuration file matching the user parameters if it exists.
* Generate the initial config matching the user parameters if it does not.
* As many benchmarks as possible use the same generator.
