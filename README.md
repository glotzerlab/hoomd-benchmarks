# HOOMD-blue benchmarks

This repository contains a number of performance benchmarks for HOOMD-blue. These are run on a variety of hardware
and execution configurations and the results are stored in the repository. Jupyter notebooks summarize the results
and the rendered notebook is checked in to the repository so that it can be viewed at nbviewer.org. Links to these
benchmark results are posted on https://codeblue.umich.edu/hoomd-blue/benchmarks.html

## Running benchmarks standaline

`cd` into a benchmark directory and run the `bmark.py` file with hoomd. It will print out performance information
and overwrite a `metadata.json` file with the performance numbers and execution configuration metadata. Each benchmark
should run in serial and MPI, though some may be too big for a single GPU's memory.

```
cd microsphere
hoomd bmark.py
mpirun -n 4 bmark.py
```

## Recording results in the database

These scripts use `signac` to store benchmark runs in a database. See the job script files for various clusters
and run configurations in the root of this repository for examples of how such runs are set up.

# Benchmark setup

Each benchmark directory **requires**:

1. An initial condition in a file
2. A `bmark.py` file that executes the benchmark.
3. A `README.md` file that describes the benchmark and cites the relevant research paper.
4. An image showing off the research.

The initial condition should be an equilibrated state so that a short benchmark run is representative of typical
steps performed in the research. The benchmark should also be at a system size studied in the research to represent
it well, not artificially inflated in size. The image should be an attractive image that shows the research, it need
not be exactly the system configuration in the benchmark (though it certainly can be). The image **should not** be
identical to a published image, to avoid copyright issues.

*Optionally*, each benchmark may include:

* Scripts that generate the image
* Scripts that generate the initial condition
* Other related files...

Each benchmark script should be a *minimal* and *short* as possible. Users will look at and possibly use items from these
scripts. The benchmark should also be very understandable so readers will know exactly what is being benchmarked
and all associated parameters, so that the run may be reproduced with other software if desired.

## System size

Each benchmark is at a fixed system size which was relevant to the research performed. This means that all benchmarks
in this repository are strong-scaling benchmarks. Weak scaling benchmarks are also of interest, but those will be
stored in another repository with a different database format as they require a much different setup.

## Run length and configuration

Each benchmark should run for no more than a few minutes to make it easy for users to run them. Each should also
properly autotune kernel launch parameters before sampling performance and should set neighbor list parameters so that
`r_buff` is tuned and there are no dangerous builds.

## Database

Each benchmark run is stored in a separate directory created and managed by `signac`. Each script should write out
a `metadata.json` file with additional information, including the performance in particle-steps-per-second.

The state points variables for `signac` are:

* `benchmark`: benchmark name (directory name).
* `cpu`: name of the CPU processor the benchmark is executed on.
* `system`: name of the system this benchmark is run on. Host name if it is an individual system, or the name of the
            cluster.
* `date`: date the benchmark is executed `date +%Y/%m/%d`
* `name`: an additional name to delineate multiple runs on the same cluster on the same day, not read or interpreted for
          analysis. For example, `cpu16`, `gpu0`, `gpu1`.

Additional information of interest, such as the GPU name, number of ranks, code version, etc... will be extracted from
the metadata dump during analysis.
