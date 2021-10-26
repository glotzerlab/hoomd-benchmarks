# Copyright (c) 2021 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Hard sphere Monte Carlo benchmark."""

import hoomd
from . import common
from .configuration.hard_sphere import make_hard_sphere_configuration


class MicrobenchmarkEmptySimulation(common.Benchmark):
    """Measure the time per step in an empty Simulation.

    See Also:
        `common.Benchmark`
    """

    def make_simulations(self):
        """Make the Simulation object."""
        path = make_hard_sphere_configuration(N=self.N,
                                              rho=self.rho,
                                              dimensions=self.dimensions,
                                              device=self.device,
                                              verbose=self.verbose)

        sim = hoomd.Simulation(device=self.device, seed=100)
        sim.create_state_from_gsd(filename=str(path))
        sim.operations.updaters.clear()
        sim.operations.computes.clear()
        sim.operations.writers.clear()
        sim.operations.tuners.clear()

        self.units = 'nanoseconds per step'

        return [sim]

    def get_performance(self):
        """Get the benchmark performance."""
        sim = self.simulations[0]
        return 1 / sim.tps / 1e-9


if __name__ == '__main__':
    MicrobenchmarkEmptySimulation.main()
