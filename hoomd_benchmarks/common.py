# Copyright (c) 2021 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Common code used in all benchmarks."""

import hoomd
import argparse
import numpy

DEFAULT_WARMUP_STEPS = 1000
DEFAULT_BENCHMARK_STEPS = 1000
DEFAULT_REPEAT = 1
DEFAULT_N = 64000
DEFAULT_RHO = 1.0
DEFAULT_DIMENSIONS = 3


def make_hoomd_device(args):
    """Initialize a HOOMD device given the parse arguments."""
    if args.device == 'CPU':
        device = hoomd.device.CPU()
    elif args.device == 'GPU':
        device = hoomd.device.GPU()
    else:
        raise ValueError(f'Invalid device {args.device}.')

    if not args.verbose:
        device.notice_level = 0

    return device


class Benchmark:
    """Base class for benchmarks.

    Args:
        device (hoomd.device.Device): Device to execute on.

        N (int): The number of particles.

        rho (float): The number density.

        dimensions (int): The number of dimensions (2 or 3).

        warmup_steps (int): Number of time steps to execute before timing
          starts.

        benchmark_steps (int): Number of time steps to execute for each
          repetition of the benchmark.

        repeat (int): Number of times to repeat the run of benchmark steps.

        verbose (bool): Set to True to see detailed output.

    Derived classes must initialize a Simulation object in ``make_simulation``
    and return it. Derived classes may also override the default
    `get_performance`, `units`, `make_argument_parser`, and `run`.

    Note:
        Derived classes may only add arguments to the argument parser created
        by `Benchmark`.

    Attributes:
        sim (hoomd.Simulation): Simulation to execute.

        units (str): Name of the units to report on the performance (only
          shown when verbose=True.
    """

    def __init__(self,
                 device,
                 N=DEFAULT_N,
                 rho=DEFAULT_RHO,
                 dimensions=DEFAULT_DIMENSIONS,
                 warmup_steps=DEFAULT_WARMUP_STEPS,
                 benchmark_steps=DEFAULT_BENCHMARK_STEPS,
                 repeat=DEFAULT_REPEAT,
                 verbose=False):
        self.device = device
        self.N = N
        self.rho = rho
        self.dimensions = dimensions
        self.warmup_steps = warmup_steps
        self.benchmark_steps = benchmark_steps
        self.repeat = repeat
        self.verbose = verbose
        self.units = 'time steps per second'
        self.sim = self.make_simulation()

    def make_simulation(self):
        """Override this method to initialize the simulation."""
        pass

    def get_performance(self):
        """Get the performance of the benchmark during the last ``run``."""
        return self.sim.tps

    def run(self, steps):
        """Run the benchmark for the given number of steps."""
        self.sim.run(steps)

    def execute(self):
        """Execute the benchmark and report the performance.

        Returns:
            list[float]: The performance measured at each benchmark stage.
        """
        print_verbose_messages = (self.verbose
                                  and self.device.communicator.rank == 0)

        if print_verbose_messages:
            print(f'Running {type(self).__name__} benchmark')

        if isinstance(self.device, hoomd.device.GPU):
            if print_verbose_messages:
                print('.. autotuning GPU kernel parameters for '
                      f'{self.warmup_steps} steps')
            self.run(self.warmup_steps)
            # TODO: Run until autotuning is complete when the autotuning API is
            # implemented.
        else:
            if print_verbose_messages:
                print(f'.. warming up for {self.warmup_steps} steps')
            self.run(self.warmup_steps)

        if print_verbose_messages:
            print(f'.. running for {self.benchmark_steps} steps '
                  f'{self.repeat} time(s)')

        # benchmark
        performance = []

        if isinstance(self.device, hoomd.device.GPU):
            with self.device.enable_profiling():
                for i in range(self.repeat):
                    self.run(self.benchmark_steps)
                    performance.append(self.get_performance())
                    if print_verbose_messages:
                        print(f'.. {performance[-1]} {self.units}')
        else:
            for i in range(self.repeat):
                self.run(self.benchmark_steps)
                performance.append(self.get_performance())
                if print_verbose_messages:
                    print(f'.. {performance[-1]} {self.units}')

        return performance

    @staticmethod
    def make_argument_parser():
        """Make an ArgumentParser instance for benchmark options."""
        parser = argparse.ArgumentParser()
        parser.add_argument('--device',
                            type=str,
                            choices=['CPU', 'GPU'],
                            help='Execution device.',
                            required=True)
        parser.add_argument('-N',
                            type=int,
                            default=DEFAULT_N,
                            help='Number of particles.')
        parser.add_argument('--rho',
                            type=float,
                            default=DEFAULT_RHO,
                            help='Number density.')
        parser.add_argument('--dimensions',
                            type=int,
                            choices=[2, 3],
                            help='Number of dimensions.',
                            default=DEFAULT_DIMENSIONS)
        parser.add_argument('--warmup_steps',
                            type=int,
                            default=DEFAULT_WARMUP_STEPS,
                            help='Number of timesteps to run to warm up stage.')
        parser.add_argument('--benchmark_steps',
                            type=int,
                            default=DEFAULT_BENCHMARK_STEPS,
                            help='Number of timesteps to run in the benchmark.')
        parser.add_argument('--repeat',
                            type=int,
                            default=DEFAULT_REPEAT,
                            help='Number of times to repeat the run.')
        parser.add_argument('-v',
                            '--verbose',
                            action='store_true',
                            help='Verbose output.')
        return parser

    @classmethod
    def main(cls):
        """Implement the command line entrypoint for benchmarks."""
        parser = cls.make_argument_parser()
        args = parser.parse_args()
        args.device = make_hoomd_device(args)
        benchmark = cls(**vars(args))
        performance = benchmark.execute()

        if args.device.communicator.rank == 0:
            print(f'{numpy.mean(performance)}')


class ComparativeBenchmark(Benchmark):
    """Base class for benchmarks that compare two simulation runs.

    Derived classes should override `make_simulations` and return a pair of
    simulations to compare.
    """

    def make_simulation(self):
        """Call make_simulations and return the first simulation."""
        self.units = 'nanoseconds per step'
        self.reference_sim, self.compare_sim = self.make_simulations()
        return self.reference_sim

    def run(self, steps):
        """Run the benchmark for the given number of steps."""
        self.reference_sim.run(steps)
        self.compare_sim.run(steps)

    def make_simulations(self):
        """Override this method to initialize the simulations."""
        pass

    def get_performance(self):
        """Get the benchmark performance."""
        t0 = 1 / self.reference_sim.tps / 1e-9
        t1 = 1 / self.compare_sim.tps / 1e-9
        return t1 - t0
