# Copyright (c) 2021-2025 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Hard sphere Monte Carlo benchmark."""

import math

import hoomd

from . import common, hpmc_base
from .configuration.hard_sphere import make_hard_sphere_configuration

DEFAULT_N_VERTICES = 6


class HPMCRegularPolygon(hpmc_base.HPMCBenchmark):
    """Hard particle Monte Carlo regular polygon benchmark.

    Args:
        n_vertices (int): Number of vertices in the regular polygon.

    See Also:
        `hpmc_base.HPMCBenchmark`
    """

    def __init__(
        self,
        n_vertices=DEFAULT_N_VERTICES,
        **kwargs,
    ):
        self.n_vertices = n_vertices
        super().__init__(**kwargs)

    @staticmethod
    def make_argument_parser():
        """Make an ArgumentParser instance for benchmark options."""
        parser = common.Benchmark.make_argument_parser()
        parser.add_argument(
            '--n_vertices',
            type=int,
            default=DEFAULT_N_VERTICES,
            help='Number of vertices in the regular polygon.',
        )

        return parser

    def make_simulation(self):
        """Make the Simulation object."""
        # Regular polygons exist only in 2D - ignore the dimensions argument.

        path = make_hard_sphere_configuration(
            N=self.N,
            rho=self.rho,
            dimensions=2,
            device=self.device,
            verbose=self.verbose,
        )

        mc = hoomd.hpmc.integrate.ConvexPolygon()
        vertices = []
        delta_theta = 2.0 * math.pi / self.n_vertices
        for i in range(self.n_vertices):
            vertices.append(
                (math.cos(delta_theta * i) / 2, math.sin(delta_theta * i) / 2)
            )

        mc.shape['A'] = dict(vertices=vertices)

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
    HPMCRegularPolygon.main()
