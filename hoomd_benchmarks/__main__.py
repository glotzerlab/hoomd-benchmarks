# Copyright (c) 2021-2023 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Command line entrypoint for the package."""

import copy
import fnmatch
import os

import hoomd
import numpy
import pandas

from . import common
from .hpmc_octahedron import HPMCOctahedron
from .hpmc_pair_lj import HPMCPairLJ
from .hpmc_pair_union_wca import HPMCPairUnionWCA
from .hpmc_sphere import HPMCSphere
from .md_pair_lj import MDPairLJ
from .md_pair_opp import MDPairOPP
from .md_pair_table import MDPairTable
from .md_pair_wca import MDPairWCA
from .microbenchmark_box_resize import MicrobenchmarkBoxResize
from .microbenchmark_custom_force import MicrobenchmarkCustomForce
from .microbenchmark_custom_trigger import MicrobenchmarkCustomTrigger
from .microbenchmark_custom_updater import MicrobenchmarkCustomUpdater
from .microbenchmark_empty_simulation import MicrobenchmarkEmptySimulation
from .microbenchmark_force_array_access import MicrobenchmarkForceArrayAccess
from .microbenchmark_get_snapshot import MicrobenchmarkGetSnapshot
from .microbenchmark_set_snapshot import MicrobenchmarkSetSnapshot
from .write_gsd import GSD
from .write_gsd_log import GSDLog
from .write_hdf5_log import HDF5Log

benchmark_classes = [
    HPMCSphere,
    HPMCOctahedron,
    HPMCPairLJ,
    HPMCPairUnionWCA,
    MDPairLJ,
    MDPairOPP,
    MDPairTable,
    MDPairWCA,
    MicrobenchmarkBoxResize,
    MicrobenchmarkEmptySimulation,
    MicrobenchmarkCustomTrigger,
    MicrobenchmarkCustomUpdater,
    MicrobenchmarkCustomForce,
    MicrobenchmarkGetSnapshot,
    MicrobenchmarkSetSnapshot,
    MicrobenchmarkForceArrayAccess,
    GSD,
    GSDLog,
    HDF5Log,
]

parser = common.Benchmark.make_argument_parser()
parser.add_argument(
    '--benchmarks',
    type=str,
    default='*',
    help='Select the benchmarks to run by class name using ' '`fnmatch` syntax',
)
parser.add_argument(
    '-o',
    '--output',
    type=str,
    help='Add row of benchmark results to or create the output ' 'CSV file.',
)
parser.add_argument(
    '--name',
    type=str,
    default=None,
    help='Name identifying this benchmark run'
    ' (leave unset to use the HOOMD-blue version).',
)
args = parser.parse_args()

benchmark_args_ref = copy.deepcopy(vars(args))
del benchmark_args_ref['benchmarks']
del benchmark_args_ref['output']
del benchmark_args_ref['name']

device = common.make_hoomd_device(args)
benchmark_args_ref['device'] = device

performance = {}

for benchmark_class in benchmark_classes:
    # scale the benchmark_steps by the class specific scale factor
    benchmark_args = copy.copy(benchmark_args_ref)
    benchmark_args['warmup_steps'] *= benchmark_class.SUITE_STEP_SCALE
    benchmark_args['benchmark_steps'] *= benchmark_class.SUITE_STEP_SCALE

    name = benchmark_class.__name__
    if fnmatch.fnmatch(name, args.benchmarks) and benchmark_class.runs_on_device(
        device
    ):
        benchmark = benchmark_class(**benchmark_args)
        performance[name] = benchmark.execute()

        if args.output is None and benchmark_args['device'].communicator.rank == 0:
            print(f'{name}: {numpy.mean(performance[name])}')

if args.output is not None and benchmark_args['device'].communicator.rank == 0:
    performance_mean = {}
    for name, performance_list in performance.items():
        performance_mean[name] = numpy.mean(performance_list)

    name = args.name
    if name is None:
        name = hoomd.version.version
    df = pandas.DataFrame.from_dict(performance_mean, orient='index', columns=[name])

    if os.path.isfile(args.output):
        df_old = pandas.read_csv(args.output, index_col=0)
        df = df_old.join(df, how='outer')

    with open(args.output, 'w') as f:
        f.write(df.to_csv())

    if args.verbose:
        print(df)
