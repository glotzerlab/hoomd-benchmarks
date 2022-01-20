# Copyright (c) 2021-2022 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Custom Force benchmark."""

import hoomd
from . import common
from .configuration.hard_sphere import make_hard_sphere_configuration


class EmptyForce(hoomd.md.force.Custom):
    """Custom force which calls an empty set_forces method."""

    def __init__(self):
        super().__init__()

    def set_forces(self, timestep):
        """Set the forces."""
        pass


class MicrobenchmarkCustomForce(common.ComparativeBenchmark):
    """Measure the overhead of using a custom force.

    This benchmark performs an
    """

    def make_simulations(self):
        """Make the simulation objects."""
        path = make_hard_sphere_configuration(N=self.N,
                                              rho=self.rho,
                                              dimensions=self.dimensions,
                                              device=self.device,
                                              verbose=self.verbose)

        sim0 = hoomd.Simulation(device=self.device, seed=100)
        sim0.create_state_from_gsd(filename=str(path))
        sim0.operations.updaters.clear()
        sim0.operations.computes.clear()
        sim0.operations.writers.clear()
        sim0.operations.tuners.clear()
        sim0.operations.integrator = hoomd.md.Integrator(
            dt=0.001, methods=[hoomd.md.methods.NVE(filter=hoomd.filter.All())])

        sim1 = hoomd.Simulation(device=self.device, seed=100)
        sim1.create_state_from_gsd(filename=str(path))
        sim1.operations.updaters.clear()
        sim1.operations.computes.clear()
        sim1.operations.writers.clear()
        sim1.operations.tuners.clear()
        sim1.operations.integrator = hoomd.md.Integrator(
            dt=0.001, methods=[hoomd.md.methods.NVE(filter=hoomd.filter.All())])

        empty_custom_force = EmptyForce()
        sim1.operations.integrator.forces.append(empty_custom_force)

        return sim0, sim1


if __name__ == '__main__':
    MicrobenchmarkCustomForce.main()
