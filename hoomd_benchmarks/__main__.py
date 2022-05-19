# Copyright (c) 2021-2022 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Command line entrypoint for the package."""

import copy
import fnmatch
import numpy
import os
import pandas
import hoomd

from . import common
from .hpmc_sphere import HPMCSphere
from .md_pair_lj import MDPairLJ
from .md_pair_wca import MDPairWCA
from .microbenchmark_empty_simulation import MicrobenchmarkEmptySimulation
from .microbenchmark_custom_trigger import MicrobenchmarkCustomTrigger
from .microbenchmark_custom_updater import MicrobenchmarkCustomUpdater
from .microbenchmark_custom_force import MicrobenchmarkCustomForce
from .microbenchmark_get_snapshot import MicrobenchmarkGetSnapshot
from .microbenchmark_set_snapshot import MicrobenchmarkSetSnapshot

benchmark_classes = [
    HPMCSphere,
    MDPairLJ,
    MDPairWCA,
    MicrobenchmarkEmptySimulation,
    MicrobenchmarkCustomTrigger,
    MicrobenchmarkCustomUpdater,
    MicrobenchmarkCustomForce,
    MicrobenchmarkGetSnapshot,
    MicrobenchmarkSetSnapshot,
]

parser = common.Benchmark.make_argument_parser()
parser.add_argument('--benchmarks',
                    type=str,
                    default='*',
                    help='Select the benchmarks to run by class name using '
                    '`fnmatch` syntax')
parser.add_argument('-o',
                    '--output',
                    type=str,
                    help='Add row of benchmark results to or create the output '
                    'CSV file.')
parser.add_argument('--name',
                    type=str,
                    default=None,
                    help='Name identifying this benchmark run'
                    ' (leave unset to use the HOOMD-blue version).')
args = parser.parse_args()

benchmark_args_ref = copy.deepcopy(vars(args))
del benchmark_args_ref['benchmarks']
del benchmark_args_ref['output']
del benchmark_args_ref['name']
benchmark_args_ref['device'] = common.make_hoomd_device(args)

performance = {}

for benchmark_class in benchmark_classes:
    # scale the benchmark_steps by the class specific scale factor
    benchmark_args = copy.copy(benchmark_args_ref)
    benchmark_args['warmup_steps'] *= benchmark_class.SUITE_STEP_SCALE
    benchmark_args['benchmark_steps'] *= benchmark_class.SUITE_STEP_SCALE

    name = benchmark_class.__name__
    if fnmatch.fnmatch(name, args.benchmarks):
        benchmark = benchmark_class(**benchmark_args)
        performance[name] = benchmark.execute()

        if (args.output is None
                and benchmark_args['device'].communicator.rank == 0):
            print(f'{name}: {numpy.mean(performance[name])}')

if args.output is not None and benchmark_args['device'].communicator.rank == 0:
    performance_mean = {}
    for name, performance_list in performance.items():
        performance_mean[name] = numpy.mean(performance_list)

    name = args.name
    if name is None:
        name = hoomd.version.version
    df = pandas.DataFrame.from_dict(performance_mean,
                                    orient='index',
                                    columns=[name])

    if os.path.isfile(args.output):
        df_old = pandas.read_csv(args.output, index_col=0)
        df = df_old.join(df)

    with open(args.output, 'w') as f:
        f.write(df.to_csv())

    if args.verbose:
        print(df)
