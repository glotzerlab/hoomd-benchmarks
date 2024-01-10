# Copyright (c) 2021-2023 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Base class HPMC benchmark."""

from . import common


class HPMCBenchmark(common.Benchmark):
    """Base class HPMC benchmark.

    Computes performance in sweeps per second and prints out MC diagnostic information
    in verbose mode.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.units = 'sweeps per second'

    def get_performance(self):
        """Get the performance in sweeps per second."""
        return self.sim.operations.integrator.mps / self.sim.state.N_particles

    def run(self, steps):
        """Run the benchmark and report HPMC specific info in verbose mode."""
        super().run(steps)

        if self.verbose and steps > 0:
            t = self.sim.operations.integrator.translate_moves
            r = self.sim.operations.integrator.rotate_moves
            self.device.notice(f'.. translate acceptance: {t[0] / sum(t)}')
            if sum(r) > 0:
                self.device.notice(f'.. rotate acceptance: {r[0] / sum(r)}')

            overlap_checks = self.sim.operations.integrator.counters.overlap_checks
            overlap_checks /= sum(t) + sum(r)
            self.device.notice(f'.. overlap checks per trial move: {overlap_checks}')
