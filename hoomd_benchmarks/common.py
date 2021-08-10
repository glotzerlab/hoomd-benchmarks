"""Common code used in all benchmarks."""

import hoomd
import argparse

DEFAULT_WARMUP_STEPS = 1000
DEFAULT_BENCHMARK_STEPS = 1000
DEFAULT_REPEAT = 1


def make_common_argument_parser():
    """Make an ArgumentParser instance with options common to all benchmarks."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--device',
                        type=str,
                        choices=['CPU', 'GPU'],
                        help='Execution device.',
                        required=True)
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


def update_common_defaults(args):
    """Update a dictionary with default values.

    Use when passing arguments to function by parameters and not parsing the
    command line arguments.
    """
    args.setdefault('warmup_steps', DEFAULT_WARMUP_STEPS)
    args.setdefault('benchmark_steps', DEFAULT_BENCHMARK_STEPS)
    args.setdefault('repeat', DEFAULT_REPEAT)
    args.setdefault('verbose', False)
    return args


def run_simulation_benchmark(sim,
                             get_performance,
                             warmup_steps=DEFAULT_WARMUP_STEPS,
                             benchmark_steps=DEFAULT_BENCHMARK_STEPS,
                             repeat=DEFAULT_REPEAT,
                             verbose=False,
                             units="time steps per second"):
    """Run the simulation and report the performance.

    Args:
        sim (hoomd.Simulation): Simulation to execute.

        get_performance (callable): Function that returns the performance of the
          simulation.

        warmup_steps (int): Number of time steps to execute before timing
          starts.

        benchmark_steps (int): Number of time steps to execute for each
          repetition of the benchmark.

        verbose (bool): Set to True to see detailed output.

        units (str): Name of the units to report on the performance (only
          shown when verbose=True.

    Returns:
        list[float]: The performance measured at each benchmark stage.
    """
    print_verbose_messages = verbose and sim.device.communicator.rank == 0

    if isinstance(sim.device, hoomd.device.GPU):
        if print_verbose_messages:
            print('.. autotuning GPU kernel parameters for '
                  f'{warmup_steps} steps')
        sim.run(warmup_steps)
        # TODO: Run until autotuning is complete when the autotuning API is
        # implemented.
    else:
        if print_verbose_messages:
            print(f'.. warming up for {warmup_steps} steps')
        sim.run(warmup_steps)

    if print_verbose_messages:
        print(f'.. running for {benchmark_steps} steps {repeat} time(s)')

    # benchmark
    performance = []

    if isinstance(sim.device, hoomd.device.GPU):
        with sim.device.enable_profiling():
            for i in range(repeat):
                sim.run(benchmark_steps)
                performance.append(get_performance(sim))
                if print_verbose_messages:
                    print(f'.. {performance[-1]} {units}')
    else:
        for i in range(repeat):
            sim.run(benchmark_steps)
            performance.append(get_performance(sim))
            if print_verbose_messages:
                print(f'.. {performance[-1]} {units}')

    return performance
