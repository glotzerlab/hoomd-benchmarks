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
    `get_performance`, `units`, and `make_argument_parser`.

    Note:
        Derived classes may only add arguments to the argument parser.

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
        """Get the performance of the benchmark during the last ``sim.run``."""
        return self.sim.tps

    def run(self):
        """Run the simulation and report the performance.

        Returns:
            list[float]: The performance measured at each benchmark stage.
        """
        print_verbose_messages = (self.verbose
                                  and self.sim.device.communicator.rank == 0)

        if print_verbose_messages:
            print(f'Running {type(self).__name__} benchmark')

        if isinstance(self.sim.device, hoomd.device.GPU):
            if print_verbose_messages:
                print('.. autotuning GPU kernel parameters for '
                      f'{self.warmup_steps} steps')
            self.sim.run(self.warmup_steps)
            # TODO: Run until autotuning is complete when the autotuning API is
            # implemented.
        else:
            if print_verbose_messages:
                print(f'.. warming up for {self.warmup_steps} steps')
            self.sim.run(self.warmup_steps)

        if print_verbose_messages:
            print(f'.. running for {self.benchmark_steps} steps '
                  f'{self.repeat} time(s)')

        # benchmark
        performance = []

        if isinstance(self.sim.device, hoomd.device.GPU):
            with self.sim.device.enable_profiling():
                for i in range(self.repeat):
                    self.sim.run(self.benchmark_steps)
                    performance.append(self.get_performance())
                    if print_verbose_messages:
                        print(f'.. {performance[-1]} {self.units}')
        else:
            for i in range(self.repeat):
                self.sim.run(self.benchmark_steps)
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
        performance = benchmark.run()

        if args.device.communicator.rank == 0:
            print(f'{numpy.mean(performance)}')
