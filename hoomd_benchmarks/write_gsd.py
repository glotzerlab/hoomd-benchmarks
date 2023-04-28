# Copyright (c) 2021-2023 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Benchmark GSD writes."""

import hoomd
import time
from . import common
from .configuration.hard_sphere import make_hard_sphere_configuration

DEFAULT_BANDWIDTH = 'false'
DEFAULT_MAXIMUM_WRITE_BUFFER_SIZE = 64 * 1024 * 1024


class GSD(common.Benchmark):
    """Base class GSD benchmark.

    Args:
        kwargs: Keyword arguments accepted by ``Benchmark.__init__``

    Derived classes should set override `make_write_gsd` to implement
    different options.

    See Also:
        `common.Benchmark`
    """

    def __init__(self,
                 bandwidth=DEFAULT_BANDWIDTH,
                 maximum_write_buffer_size=DEFAULT_MAXIMUM_WRITE_BUFFER_SIZE,
                 **kwargs):
        self.bandwidth = bandwidth
        self.maximum_write_buffer_size = maximum_write_buffer_size

        super().__init__(**kwargs)

        if bandwidth:
            self.units = 'MiB/s'

    @staticmethod
    def make_argument_parser():
        """Make an ArgumentParser instance for benchmark options."""
        parser = common.Benchmark.make_argument_parser()
        parser.add_argument('--bandwidth',
                            action='store_true',
                            help='Report performance in bandwidth.')
        parser.add_argument('--maximum_write_buffer_size',
                            type=int,
                            default=DEFAULT_MAXIMUM_WRITE_BUFFER_SIZE,
                            help='Maximum size of the write buffer (in bytes).')
        return parser

    def make_write_gsd(self):
        """Make the GSD writer object for benchmarking."""
        writer = hoomd.write.GSD(trigger=hoomd.trigger.Periodic(1),
                                 filename='write_gsd.gsd',
                                 mode='wb')

        try:
            writer.dynamic = ['particles/position']
        except hoomd.error.TypeConversionError:
            pass

        return writer

    def make_simulation(self):
        """Make the Simulation object."""
        path = make_hard_sphere_configuration(N=self.N,
                                              rho=self.rho,
                                              dimensions=self.dimensions,
                                              device=self.device,
                                              verbose=self.verbose)

        sim = hoomd.Simulation(device=self.device)
        sim.create_state_from_gsd(filename=str(path))

        self.writer = self.make_write_gsd()
        self.writer.maximum_write_buffer_size = self.maximum_write_buffer_size
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
            return self.N * 4 * 3 / 1024**2 * self.tps
        else:
            return self.tps


if __name__ == '__main__':
    GSD.main()
