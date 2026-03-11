# Copyright (c) 2021-2026 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Hard ellipsoid Monte Carlo benchmark."""

import math

import hoomd

from . import hpmc_base
from .configuration.hard_shape import make_hard_shape_configuration


class HPMCEllipsoid(hpmc_base.HPMCBenchmark):
    """Hard particle Monte Carlo octahedron benchmark.

    See Also:
        `hpmc_base.HPMCBenchmark`
    """

    def make_simulation(self):
        """Make the Simulation object."""
        shape = dict(a=2.5, b=0.5, c=0.5)
        mc = hoomd.hpmc.integrate.Ellipsoid()
        mc.shape['A'] = shape
        
        ellipsoid_volume = 4.0 / 3.0 * math.pi * 2.5 * 0.5 * 0.5;

        path = make_hard_shape_configuration(
            name="ellipsoid",
            N=self.N,
            integrator=mc,
            phi=0.5,
            particle_volume=ellipsoid_volume,
            dimensions=3,
            device=self.device,
            verbose=self.verbose,
            spacing=6.0,
        )

        mc = hoomd.hpmc.integrate.Ellipsoid(default_d=0.03662120237875685, default_a=0.019755985607527712)
        mc.shape['A'] = shape

        sim = hoomd.Simulation(device=self.device, seed=100)
        sim.create_state_from_gsd(filename=str(path))
        sim.operations.integrator = mc

        return sim


if __name__ == '__main__':
    HPMCEllipsoid.main()
