# HOOMD-blue benchmarks

This repository contains a number of performance benchmarks for HOOMD-blue. These are run on a variety of hardware
and execution configurations and the results are stored as [signac](http://signac.io) job documents.

## Prerequistes

* [signac and signac-flow (groups branch)](http://signac.io)
* [HOOMD-blue (next branch)](http://glotzerlab.engin.umich.edu/hoomd-blue)

## Running benchmarks standalone

To submit all benchmarks as cluster jobs,

```
python project.py submit --exec
```

or, to extract the command lines of the individual operations
```
python project.py submit --exec --test
```
and then execute those operations interactively.

You can modify the list of requested hardware configurations in the file `exec_confs.py`.

To run a benchmark with a different system size than the default, `cd` into a benchmark directory and follow the steps in `README.md`.
Some tests can be configured with variable number of particles, others assume a fixed number. Example for LJ liquid benchmark:

```
cd lj-liquid
python init.py 64 # generate a state point with 64**3 = 262144 particles.
```

Then follow the above steps to execute the operations on the new state point.

## Querying the results in the signac database

These scripts use `signac` to store benchmark runs in a database, with the job document holding the performance
results for a specific system size and execution configuration. Query the results with

```
signac document
```

# Benchmark setup

Each benchmark directory **requires**:

1. An `operations.py` file that defines the operations for that benchmark
2. A `README.md` file that describes the benchmark and cites the relevant research paper.
3. An image showing off the research.

The initial condition should be an equilibrated state so that a short benchmark run is representative of typical
steps performed in the research. The benchmark should also be at a system size studied in the research to represent
it well, not artificially inflated in size. The image should be an attractive image that shows the research, it need
not be exactly the system configuration in the benchmark (though it certainly can be). The image **should not** be
identical to a published image, to avoid copyright issues.

*Optionally*, each benchmark may include:

* job operations that generate the initial condition
* Other related files...

Each benchmark script should be a *minimal* and *short* as possible. Users will look at and possibly use items from these
scripts. The benchmark should also be very understandable so readers will know exactly what is being benchmarked
and all associated parameters, so that the run may be reproduced with other software if desired.

## System size

Each benchmark is either at a fixed system size relevant to the research performed. This means that all benchmarks
in with fixed system size are strong-scaling benchmarks. Some benchmarks allow initializing state points with different
system sizes through `init.py` and are therefore suitable for weak scaling.

## Run length and configuration

Each benchmark should run for no more than a few minutes to make it easy for users to run them. Each should also
properly autotune kernel launch parameters before sampling performance and should set neighbor list parameters so that
`r_buff` is tuned and there are no dangerous builds.

## Database

Each benchmark run is stored in a separate directory created and managed by `signac`. Each script should generate an entry
in the `signac_job_document.json` file with additional information, including the performance in particle-steps-per-second.
Additional information of interest, such as the GPU name, number of ranks, code version, etc... will be extracted from
the metadata dump during analysis.
