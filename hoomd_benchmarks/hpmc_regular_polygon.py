# Copyright (c) 2021-2026 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Hard sphere Monte Carlo benchmark."""

import math

import hoomd

from . import common, hpmc_base
from .configuration.hard_shape import make_hard_shape_configuration

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
        vertices = []
        delta_theta = 2.0 * math.pi / self.n_vertices
        for i in range(self.n_vertices):
            vertices.append(
                (math.cos(delta_theta * i) / 2, math.sin(delta_theta * i) / 2)
            )
        polygon_area = (
            0.5**2 * self.n_vertices * math.sin(2.0 * math.pi / self.n_vertices) / 2
        )
        print(polygon_area)

        mc = hoomd.hpmc.integrate.ConvexPolygon()
        mc.shape['A'] = dict(vertices=vertices)

        path = make_hard_shape_configuration(
            name='hexagon',
            N=self.N,
            integrator=mc,
            phi=0.68,
            particle_volume=polygon_area,
            dimensions=2,
            device=self.device,
            verbose=self.verbose,
        )

        mc = hoomd.hpmc.integrate.ConvexPolygon(
            default_d=0.2, default_a=2.0 * math.pi / 6.0
        )
        mc.shape['A'] = dict(vertices=vertices)

        sim = hoomd.Simulation(device=self.device, seed=100)
        sim.create_state_from_gsd(filename=str(path))
        sim.operations.integrator = mc

        return sim


if __name__ == '__main__':
    HPMCRegularPolygon.main()
