# Copyright (c) 2021-2023 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Hard sphere Monte Carlo benchmark."""

import hoomd

from . import common
from .configuration.hard_sphere import make_hard_sphere_configuration


class HPMCSphere(common.Benchmark):
    """Hard particle Monte Carlo sphere benchmark.

    See Also:
        `common.Benchmark`
    """

    def make_simulation(self):
        """Make the Simulation object."""
        path = make_hard_sphere_configuration(
            N=self.N,
            rho=self.rho,
            dimensions=self.dimensions,
            device=self.device,
            verbose=self.verbose,
        )

        mc = hoomd.hpmc.integrate.Sphere()
        mc.shape['A'] = dict(diameter=1.0)

        sim = hoomd.Simulation(device=self.device, seed=100)
        sim.create_state_from_gsd(filename=str(path))
        sim.operations.integrator = mc

        self.units = 'trial moves per second per particle'

        return sim

    def get_performance(self):
        """Get the benchmark performance."""
        mc = self.sim.operations.integrator
        return (
            (sum(mc.translate_moves) + sum(mc.rotate_moves))
            / self.sim.walltime
            / self.sim.state.N_particles
        )


if __name__ == '__main__':
    HPMCSphere.main()
