# Copyright (c) 2021-2023 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Common code used in all benchmarks."""

import argparse

import hoomd
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

    SUITE_STEP_SCALE = 1

    def __init__(
        self,
        device,
        N=DEFAULT_N,
        rho=DEFAULT_RHO,
        dimensions=DEFAULT_DIMENSIONS,
        warmup_steps=DEFAULT_WARMUP_STEPS,
        benchmark_steps=DEFAULT_BENCHMARK_STEPS,
        repeat=DEFAULT_REPEAT,
        verbose=False,
    ):
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
        print_verbose_messages = self.verbose and self.device.communicator.rank == 0

        # Ensure that all ops are attached (needed for is_tuning_complete).
        self.run(0)

        if print_verbose_messages:
            print(f'Running {type(self).__name__} benchmark')

        if print_verbose_messages:
            print(f'.. warming up for {self.warmup_steps} steps')
        self.run(self.warmup_steps)

        if isinstance(self.device, hoomd.device.GPU) and hasattr(
            self.sim.operations, 'is_tuning_complete'
        ):
            while not self.sim.operations.is_tuning_complete:
                if print_verbose_messages:
                    print(
                        '.. autotuning GPU kernel parameters for '
                        f'{self.warmup_steps} steps'
                    )
                self.run(self.warmup_steps)

        if print_verbose_messages:
            print(
                f'.. running for {self.benchmark_steps} steps ' f'{self.repeat} time(s)'
            )

        # benchmark
        performance = []

        if isinstance(self.device, hoomd.device.GPU):
            with self.device.enable_profiling():
                for _i in range(self.repeat):
                    self.run(self.benchmark_steps)
                    performance.append(self.get_performance())
                    if print_verbose_messages:
                        print(f'.. {performance[-1]} {self.units}')
        else:
            for _i in range(self.repeat):
                self.run(self.benchmark_steps)
                performance.append(self.get_performance())
                if print_verbose_messages:
                    print(f'.. {performance[-1]} {self.units}')

        return performance

    @staticmethod
    def make_argument_parser():
        """Make an ArgumentParser instance for benchmark options."""
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--device',
            type=str,
            choices=['CPU', 'GPU'],
            help='Execution device.',
            required=True,
        )
        parser.add_argument(
            '-N', type=int, default=DEFAULT_N, help='Number of particles.'
        )
        parser.add_argument(
            '--rho', type=float, default=DEFAULT_RHO, help='Number density.'
        )
        parser.add_argument(
            '--dimensions',
            type=int,
            choices=[2, 3],
            help='Number of dimensions.',
            default=DEFAULT_DIMENSIONS,
        )
        parser.add_argument(
            '--warmup_steps',
            type=int,
            default=DEFAULT_WARMUP_STEPS,
            help='Number of timesteps to run before timing.',
        )
        parser.add_argument(
            '--benchmark_steps',
            type=int,
            default=DEFAULT_BENCHMARK_STEPS,
            help='Number of timesteps to run in the benchmark.',
        )
        parser.add_argument(
            '--repeat',
            type=int,
            default=DEFAULT_REPEAT,
            help='Number of times to repeat the run.',
        )
        parser.add_argument(
            '-v', '--verbose', action='store_true', help='Verbose output.'
        )
        return parser

    @classmethod
    def runs_on_device(cls, device):
        """Returns True when the benchmark can be run on the given device."""
        return True

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
    simulations to compare. `get_performance` takes the difference
    time difference between the reference and compare simulations and returns
    the inverse. This is a measure of how many times the overhead in the compare
    simulation can be called per second.

    See Also:
        `common.Benchmark`
    """

    def __init__(self, skip_reference=False, **kwargs):
        self.skip_reference = skip_reference
        super().__init__(**kwargs)

    def make_simulation(self):
        """Call make_simulations and return the first simulation."""
        if self.skip_reference:
            self.units = 'time steps per second'
        else:
            self.units = 'calls per second'

        self.reference_sim, self.compare_sim = self.make_simulations()
        return self.reference_sim

    def run(self, steps):
        """Run the benchmark for the given number of steps."""
        if not self.skip_reference:
            self.reference_sim.run(steps)
        self.compare_sim.run(steps)

    def make_simulations(self):
        """Override this method to initialize the simulations."""
        pass

    def get_performance(self):
        """Get the benchmark performance."""
        if self.skip_reference:
            return self.compare_sim.tps

        # Avoid divide by zero errors when the simulation is not executed.
        if self.reference_sim.tps == 0:
            return 0

        t0 = 1 / self.reference_sim.tps
        t1 = 1 / self.compare_sim.tps
        return 1 / (t1 - t0)

    @staticmethod
    def make_argument_parser():
        """Make an ArgumentParser instance for comparative benchmark options."""
        parser = Benchmark.make_argument_parser()
        parser.add_argument(
            '--skip-reference',
            action='store_true',
            help='Skip the reference simulation run.',
        )
        return parser
