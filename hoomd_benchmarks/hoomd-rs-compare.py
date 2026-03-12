# Copyright (c) 2021-2026 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Command line entrypoint for the package."""

import os

import hoomd
import numpy
import pandas

from . import common
from .hpmc_ellipsoid import HPMCEllipsoid
from .hpmc_octahedron import HPMCOctahedron
from .hpmc_pair_lj import HPMCPairLJ
from .hpmc_regular_polygon import HPMCRegularPolygon
from .hpmc_sphere import HPMCSphere

device = hoomd.device.CPU()
results = pandas.DataFrame(columns=['benchmark', 'n', 'threads', 'time_per_operation'])

threads = device.communicator.num_ranks

for n in [1024, 2048, 4096, 8192, 16384, 32768, 65536]:

    steps = max(int(1000 * 1024 / n * threads), 1)
    common_args = { 'device': device, 'N': n, 'verbose': True, 'warmup_steps': steps, 'benchmark_steps': steps }

    benchmarks = {"mc_2d_sphere": HPMCSphere(dimensions=2, **common_args),
        "mc_2d_lennard_jones": HPMCPairLJ(dimensions=2, **common_args),
        "mc_2d_hexagon": HPMCRegularPolygon(**common_args),
        "mc_3d_sphere": HPMCSphere(dimensions=3, **common_args),
        "mc_3d_lennard_jones": HPMCPairLJ(dimensions=3, **common_args),
        "mc_3d_octahedron": HPMCOctahedron(**common_args),
        "mc_3d_ellipsoid": HPMCEllipsoid(**common_args),
    }

    for (name, benchmark) in benchmarks.items():
        try:    
            performance = numpy.mean(benchmark.execute())
        except:
            continue
                
        row = { 'benchmark': name,
                'n': n,
                'threads': threads,
                'time_per_operation': 1.0 / performance,
            }
        if device.communicator.rank == 0:
            print(f'{name}: {performance}')

        results.loc[len(results)] = row

if device.communicator.rank == 0:
    filename = f"hoomd-blue-anvil-{threads}.csv"
    with open(filename, 'w') as f:
        f.write(results.to_csv())

    print(results)
