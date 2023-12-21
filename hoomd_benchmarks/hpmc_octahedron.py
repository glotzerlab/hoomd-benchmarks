# Copyright (c) 2021-2023 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Hard octahedron Monte Carlo benchmark."""

import hoomd

from . import hpmc_base
from .configuration.hard_sphere import make_hard_sphere_configuration


class HPMCOctahedron(hpmc_base.HPMCBenchmark):
    """Hard particle Monte Carlo octahedron benchmark.

    See Also:
        `hpmc_base.HPMCBenchmark`
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

        mc = hoomd.hpmc.integrate.ConvexPolyhedron()
        mc.shape['A'] = dict(
            vertices=[
                (-0.5, 0, 0),
                (0.5, 0, 0),
                (0, -0.5, 0),
                (0, 0.5, 0),
                (0, 0, -0.5),
                (0, 0, 0.5),
            ]
        )

        sim = hoomd.Simulation(device=self.device, seed=100)
        sim.create_state_from_gsd(filename=str(path))
        sim.operations.integrator = mc

        return sim

if __name__ == '__main__':
    HPMCOctahedron.main()
