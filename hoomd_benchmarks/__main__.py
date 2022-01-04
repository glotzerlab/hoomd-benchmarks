# Copyright (c) 2021-2022 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Command line entrypoint for the package."""

import copy
import fnmatch
import numpy
import os
import pandas

from . import common
from .hpmc_sphere import HPMCSphere
from .md_pair_lj import MDPairLJ
from .md_pair_wca import MDPairWCA
from .microbenchmark_empty_simulation import MicrobenchmarkEmptySimulation
from .microbenchmark_custom_trigger import MicrobenchmarkCustomTrigger
from .microbenchmark_custom_updater import MicrobenchmarkCustomUpdater
from .microbenchmark_get_snapshot import MicrobenchmarkGetSnapshot
from .microbenchmark_set_snapshot import MicrobenchmarkSetSnapshot

benchmark_classes = [
    HPMCSphere,
    MDPairLJ,
    MDPairWCA,
    MicrobenchmarkEmptySimulation,
    MicrobenchmarkCustomTrigger,
    MicrobenchmarkCustomUpdater,
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
                    help='Name identifying this benchmark run.')
args = parser.parse_args()

benchmark_args = copy.deepcopy(vars(args))
del benchmark_args['benchmarks']
del benchmark_args['output']
del benchmark_args['name']
benchmark_args['device'] = common.make_hoomd_device(args)

performance = {}

for benchmark_class in benchmark_classes:
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

    df = pandas.DataFrame.from_dict(performance_mean,
                                    orient='index',
                                    columns=[args.name])

    if os.path.isfile(args.output):
        df_old = pandas.read_csv(args.output, index_col=0)
        df = df_old.join(df)

    with open(args.output, 'w') as f:
        f.write(df.to_csv())

    if args.verbose:
        print(df)
