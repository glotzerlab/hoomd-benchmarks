# Copyright (c) 2021-2024 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Lennard-Jones HPMC pair potential benchmark."""

import hoomd
import numpy

from . import common, hpmc_base
from .configuration.hard_sphere import make_hard_sphere_configuration

DEFAULT_MODE = 'compiled'
DEFAULT_LEAF_CAPACITY = 0
DEFAULT_GRID = 4


class HPMCPairUnionWCA(hpmc_base.HPMCBenchmark):
    """Test performance of HPMC union potentials."""

    def __init__(
        self,
        mode=DEFAULT_MODE,
        leaf_capacity=DEFAULT_LEAF_CAPACITY,
        grid=DEFAULT_GRID,
        **kwargs,
    ):
        self.mode = mode
        self.leaf_capacity = leaf_capacity
        self.grid = grid
        super().__init__(**kwargs)

    @staticmethod
    def make_argument_parser():
        """Make an ArgumentParser instance for benchmark options."""
        parser = common.Benchmark.make_argument_parser()
        parser.add_argument('--mode', default=DEFAULT_MODE, help='Compute mode.')
        parser.add_argument(
            '--leaf-capacity',
            default=DEFAULT_LEAF_CAPACITY,
            help='Leaf capacity.',
            type=int,
        )
        parser.add_argument(
            '--grid',
            default=DEFAULT_GRID,
            help='Number of grid points along an edge.',
            type=int,
        )
        return parser

    @classmethod
    def runs_on_device(cls, device):
        """Returns True when the benchmark can be run on the given device."""
        if isinstance(device, hoomd.device.GPU):
            return False

        pair_class = getattr(hoomd.hpmc.pair, 'Union', None)
        if pair_class is None:
            # Skip this benchmark on HOOMD releases that lack the needed pair
            # potential.
            return False

        return True

    def make_simulation(self):
        """Make the Simulation object."""
        path = make_hard_sphere_configuration(
            N=self.N,
            rho=self.rho,
            dimensions=self.dimensions,
            device=self.device,
            verbose=self.verbose,
        )

        integrator = hoomd.hpmc.integrate.Sphere(default_d=0.3, default_a=0.4)
        integrator.shape['A'] = dict(diameter=0, orientable=True)

        sim = hoomd.Simulation(device=self.device, seed=10)
        sim.create_state_from_gsd(filename=str(path))

        sigma = 0.1
        r_cut = 2 ** (1 / 6) * sigma
        points = numpy.linspace(start=-0.5, stop=0.5, num=self.grid)
        positions = []
        positions.extend([(x, 0, 0) for x in points])
        positions.extend([(0, x, 0) for x in points])
        positions.extend([(0, 0, x) for x in points])

        if self.mode == 'compiled':
            lennard_jones = hoomd.hpmc.pair.LennardJones()
            lennard_jones.params[('A', 'A')] = dict(
                epsilon=1.0, sigma=sigma, r_cut=r_cut
            )
            lennard_jones.mode = 'shift'

            pair = hoomd.hpmc.pair.Union(
                constituent_potential=lennard_jones, leaf_capacity=self.leaf_capacity
            )
            pair.body['A'] = dict(positions=positions, types=['A'] * len(positions))

            integrator.pair_potentials = [pair]
        elif self.mode == 'code':
            code_wca = f"""
                    float rsq = dot(r_ij, r_ij);
                    float r_cut = { r_cut };
                    float r_cutsq = r_cut * r_cut;

                    if (rsq >= r_cutsq)
                        return 0.0f;

                    float sigma = { sigma };
                    float sigsq = sigma * sigma;
                    float rsqinv = sigsq / rsq;
                    float r6inv = rsqinv * rsqinv * rsqinv;
                    float r12inv = r6inv * r6inv;
                    return 4 * 1.0 * (r12inv - r6inv) + 1;
                    """

            patch = hoomd.hpmc.pair.user.CPPPotentialUnion(
                r_cut_constituent=r_cut,
                r_cut_isotropic=0.0,
                code_constituent=code_wca,
                code_isotropic='return 0;',
                param_array_constituent=[],
                param_array_isotropic=[],
            )

            patch.leaf_capacity = min(self.leaf_capacity, 1)

            patch.positions['A'] = positions
            patch.orientations['A'] = [(1, 0, 0, 0)] * len(positions)
            patch.charges['A'] = [0] * len(positions)
            patch.diameters['A'] = [0] * len(positions)
            patch.typeids['A'] = [0] * len(positions)
            integrator.pair_potential = patch
        else:
            raise ValueError('Invalid mode: ', self.mode)

        sim.operations.integrator = integrator

        return sim


if __name__ == '__main__':
    HPMCPairUnionWCA.main()
