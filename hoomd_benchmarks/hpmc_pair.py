# Copyright (c) 2021-2024 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Methods common to HPMC pair potential benchmarks."""

import hoomd

from . import common, hpmc_base
from .configuration.hard_sphere import make_hard_sphere_configuration

DEFAULT_MODE = 'compiled'


class HPMCPair(hpmc_base.HPMCBenchmark):
    """Base class HPMC pair potential benchmark.

    Args:
        mode (str): Set to 'compiled' to use a compiled pair potential. Set to
          'code' to use CPPPotential.

        kwargs: Keyword arguments accepted by ``Benchmark.__init__``

    Derived classes should set the class level variables ``pair_class``,
    ``pair_params``, ``r_cut``, and ``code``.

    See Also:
        `common.Benchmark`
    """

    pair_class_args = {}

    def __init__(
        self,
        mode=DEFAULT_MODE,
        **kwargs,
    ):
        self.mode = mode
        super().__init__(**kwargs)

    @staticmethod
    def make_argument_parser():
        """Make an ArgumentParser instance for benchmark options."""
        parser = common.Benchmark.make_argument_parser()
        parser.add_argument('--mode', default=DEFAULT_MODE, help='Compute mode.')
        return parser

    def make_simulation(self):
        """Make the Simulation object."""
        path = make_hard_sphere_configuration(
            N=self.N,
            rho=self.rho,
            dimensions=self.dimensions,
            device=self.device,
            verbose=self.verbose,
        )

        integrator = hoomd.hpmc.integrate.Sphere(default_d=0.18)
        integrator.shape['A'] = dict(diameter=self.diameter)

        sim = hoomd.Simulation(device=self.device, seed=10)
        sim.create_state_from_gsd(filename=str(path))

        if self.mode == 'compiled':
            pair = self.pair_class(**self.pair_class_args)
            pair.params[('A', 'A')] = self.pair_params
            integrator.pair_potentials = [pair]
        elif self.mode == 'code':
            patch = hoomd.hpmc.pair.user.CPPPotential(
                code=self.code, r_cut=self.r_cut, param_array=[]
            )
            integrator.pair_potential = patch
        else:
            raise ValueError('Invalid mode: ', self.mode)

        sim.operations.integrator = integrator

        return sim

    @classmethod
    def runs_on_device(cls, device):
        """Returns True when the benchmark can be run on the given device."""
        if isinstance(device, hoomd.device.GPU):
            return False

        if cls.pair_class is None:
            # Skip this benchmark on HOOMD releases that lack the needed pair
            # potential.
            return False

        return True
