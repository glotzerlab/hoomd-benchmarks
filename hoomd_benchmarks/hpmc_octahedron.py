# Copyright (c) 2021-2026 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Hard octahedron Monte Carlo benchmark."""

import math

import hoomd

from . import hpmc_base
from .configuration.hard_shape import make_hard_shape_configuration


class HPMCOctahedron(hpmc_base.HPMCBenchmark):
    """Hard particle Monte Carlo octahedron benchmark.

    See Also:
        `hpmc_base.HPMCBenchmark`
    """

    def make_simulation(self):
        """Make the Simulation object."""
        shape = dict(
            vertices=[
                (-0.5, 0, 0),
                (0.5, 0, 0),
                (0, -0.5, 0),
                (0, 0.5, 0),
                (0, 0, -0.5),
                (0, 0, 0.5),
            ]
        )
        mc = hoomd.hpmc.integrate.ConvexPolyhedron()
        mc.shape['A'] = shape
        a = math.sqrt(2.0) / 2.0
        octahedron_volume = 1.0 / 3.0 * math.sqrt(2.0) * a**3
        path = make_hard_shape_configuration(
            name='octahedron',
            N=self.N,
            integrator=mc,
            phi=0.44,
            particle_volume=octahedron_volume,
            dimensions=3,
            device=self.device,
            verbose=self.verbose,
        )

        mc = hoomd.hpmc.integrate.ConvexPolyhedron(default_d=0.081, default_a=0.20)
        mc.shape['A'] = shape

        sim = hoomd.Simulation(device=self.device, seed=100)
        sim.create_state_from_gsd(filename=str(path))
        sim.operations.integrator = mc

        return sim


if __name__ == '__main__':
    HPMCOctahedron.main()
