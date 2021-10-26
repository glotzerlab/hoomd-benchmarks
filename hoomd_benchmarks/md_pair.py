# Copyright (c) 2021 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Methods common to MD pair potential benchmarks."""

import hoomd
from . import common
from .configuration.hard_sphere import make_hard_sphere_configuration

DEFAULT_BUFFER = 0.4
DEFAULT_REBUILD_CHECK_DELAY = 1


class MDPair(common.Benchmark):
    """Base class pair potential benchmark.

    Args:
        buffer (float): Neighbor list buffer distance.

        rebuild_check_delay (int): Number of timesteps to run before checking if
          the neighbor list needs rebuilding.

        kwargs: Keyword arguments accepted by ``Benchmark.__init__``

    Derived classes should set the class level variables ``pair_class``,
    ``pair_params``, and ``r_cut``.

    See Also:
        `common.Benchmark`
    """

    def __init__(self,
                 buffer=DEFAULT_BUFFER,
                 rebuild_check_delay=DEFAULT_REBUILD_CHECK_DELAY,
                 **kwargs):
        self.buffer = buffer
        self.rebuild_check_delay = rebuild_check_delay
        super().__init__(**kwargs)

    @staticmethod
    def make_argument_parser():
        """Make an ArgumentParser instance for benchmark options."""
        parser = common.Benchmark.make_argument_parser()
        parser.add_argument('--buffer',
                            type=float,
                            default=DEFAULT_BUFFER,
                            help='Neighbor list buffer.')
        parser.add_argument('--rebuild_check_delay',
                            type=int,
                            default=DEFAULT_REBUILD_CHECK_DELAY,
                            help='Neighbor list rebuild check delay.')
        return parser

    def make_simulations(self):
        """Make the Simulation object."""
        path = make_hard_sphere_configuration(N=self.N,
                                              rho=self.rho,
                                              dimensions=self.dimensions,
                                              device=self.device,
                                              verbose=self.verbose)

        integrator = hoomd.md.Integrator(dt=0.005)
        cell = hoomd.md.nlist.Cell()
        cell.rebuild_check_delay = self.rebuild_check_delay
        cell.buffer = self.buffer

        pair = self.pair_class(nlist=cell)
        pair.params[('A', 'A')] = self.pair_params
        pair.r_cut[('A', 'A')] = self.r_cut
        integrator.forces.append(pair)
        nvt = hoomd.md.methods.NVT(kT=1.2, filter=hoomd.filter.All(), tau=0.5)
        integrator.methods.append(nvt)

        sim = hoomd.Simulation(device=self.device)
        sim.create_state_from_gsd(filename=str(path))
        sim.operations.integrator = integrator

        return [sim]
