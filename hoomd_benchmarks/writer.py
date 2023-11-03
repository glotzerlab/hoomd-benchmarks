# Copyright (c) 2021-2023 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Benchmark GSD writes."""

import hoomd
import time
from . import common
from .configuration.hard_sphere import make_hard_sphere_configuration

DEFAULT_BANDWIDTH = False


class Writer(common.Benchmark):
    """Base class Writer benchmark.

    Args:
        kwargs: Keyword arguments accepted by ``Benchmark.__init__``

    Derived classes should set override `make_writer` to implement
    different options.

    See Also:
        `common.Benchmark`
    """

    def __init__(self,
                 bandwidth=DEFAULT_BANDWIDTH,
                 **kwargs):
        self.bandwidth = bandwidth

        super().__init__(**kwargs)

        if bandwidth:
            self.units = 'MiB/s'

        self.bytes_per_step = 1

    @staticmethod
    def make_argument_parser():
        """Make an ArgumentParser instance for benchmark options."""
        parser = common.Benchmark.make_argument_parser()
        parser.add_argument('--bandwidth',
                            action='store_true',
                            help='Report performance in bandwidth.')
        return parser

    def make_writer(self):
        """Make the writer object for benchmarking."""
        pass

    def make_simulation(self):
        """Make the Simulation object."""
        path = make_hard_sphere_configuration(N=self.N,
                                              rho=self.rho,
                                              dimensions=self.dimensions,
                                              device=self.device,
                                              verbose=self.verbose)

        sim = hoomd.Simulation(device=self.device)
        sim.create_state_from_gsd(filename=str(path))

        self.writer = self.make_writer()
        sim.operations.writers.append(self.writer)

        return sim

    def run(self, steps):
        """Run the benchmark for the given number of steps."""
        start_time = time.time()

        self.sim.run(steps)
        if hasattr(self.writer, 'flush'):
            self.writer.flush()
        end_time = time.time()

        self.tps = steps / (end_time - start_time)

    def get_performance(self):
        """Get the performance of the benchmark during the last ``run``."""
        if self.bandwidth:
            return self.bytes_per_step * self.tps
        else:
            return self.tps


if __name__ == '__main__':
    GSD.main()
