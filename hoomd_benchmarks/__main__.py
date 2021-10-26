# Copyright (c) 2021 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Command line entrypoint for the package."""

from . import common
import numpy
from .hpmc_sphere import HPMCSphere
from .md_pair_lj import MDPairLJ
from .md_pair_wca import MDPairWCA
from .microbenchmark_empty_simulation import MicrobenchmarkEmptySimulation
from .microbenchmark_custom_trigger import MicrobenchmarkCustomTrigger
from .microbenchmark_custom_updater import MicrobenchmarkCustomUpdater
from .microbenchmark_get_snapshot import MicrobenchmarkGetSnapshot

benchmark_classes = [
    HPMCSphere,
    MDPairLJ,
    MDPairWCA,
    MicrobenchmarkEmptySimulation,
    MicrobenchmarkCustomTrigger,
    MicrobenchmarkCustomUpdater,
    MicrobenchmarkGetSnapshot,
]

parser = common.Benchmark.make_argument_parser()
args = parser.parse_args()
args.device = common.make_hoomd_device(args)

for benchmark_class in benchmark_classes:
    benchmark = benchmark_class(**vars(args))
    name = benchmark_class.__name__
    performance = benchmark.execute()

    if args.device.communicator.rank == 0:
        print(f'{name}: {numpy.mean(performance)}')
