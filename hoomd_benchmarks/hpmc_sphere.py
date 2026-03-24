# Copyright (c) 2021-2026 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Hard sphere Monte Carlo benchmark."""

import math

import hoomd

from . import hpmc_base
from .configuration.hard_shape import make_hard_shape_configuration


class HPMCSphere(hpmc_base.HPMCBenchmark):
    """Hard particle Monte Carlo sphere benchmark.

    See Also:
        `hpmc_base.HPMCBenchmark`
    """

    def make_simulation(self):
        """Make the Simulation object."""
        mc = hoomd.hpmc.integrate.Sphere()
        mc.shape['A'] = dict(diameter=1.0)

        r = 0.5
        if self.dimensions == 2:
            sphere_volume = math.pi * r**2
            default_d = 0.7
        if self.dimensions == 3:
            sphere_volume = 4.0 / 3.0 * math.pi * r**3
            default_d = 0.13

        path = make_hard_shape_configuration(
            name='sphere',
            N=self.N,
            integrator=mc,
            phi=0.50,
            particle_volume=sphere_volume,
            dimensions=self.dimensions,
            device=self.device,
            verbose=self.verbose,
        )

        mc = hoomd.hpmc.integrate.Sphere(default_d=default_d)
        mc.shape['A'] = dict(diameter=1.0)

        sim = hoomd.Simulation(device=self.device, seed=100)
        sim.create_state_from_gsd(filename=str(path))
        sim.operations.integrator = mc

        return sim


if __name__ == '__main__':
    HPMCSphere.main()
