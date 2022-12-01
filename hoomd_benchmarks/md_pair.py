# Copyright (c) 2021-2022 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Methods common to MD pair potential benchmarks."""

import hoomd
from . import common
from .configuration.hard_sphere import make_hard_sphere_configuration

DEFAULT_BUFFER = 0.4
DEFAULT_REBUILD_CHECK_DELAY = 1
DEFAULT_TAIL_CORRECTION = False
DEFAULT_N_TYPES = 1
DEFAULT_MODE = 'none'


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
                 tail_correction=DEFAULT_TAIL_CORRECTION,
                 n_types=DEFAULT_N_TYPES,
                 always_compute_pressure=False,
                 mode=DEFAULT_MODE,
                 **kwargs):
        self.buffer = buffer
        self.rebuild_check_delay = rebuild_check_delay
        self.tail_correction = tail_correction
        self.n_types = n_types
        self.always_compute_pressure = always_compute_pressure
        self.mode = mode
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
        parser.add_argument('--tail_correction',
                            action='store_true',
                            help='Enable integrated isotropic tail correction.')
        parser.add_argument('--n_types',
                            type=int,
                            default=DEFAULT_N_TYPES,
                            help='Number of particle types.')
        parser.add_argument('--always_compute_pressure',
                            action='store_true',
                            help='Always compute pressure.')
        parser.add_argument('--mode', default=DEFAULT_MODE, help='Shift mode.')
        return parser

    def make_simulation(self):
        """Make the Simulation object."""
        path = make_hard_sphere_configuration(N=self.N,
                                              rho=self.rho,
                                              dimensions=self.dimensions,
                                              device=self.device,
                                              verbose=self.verbose,
                                              n_types=self.n_types)

        integrator = hoomd.md.Integrator(dt=0.005)
        cell = hoomd.md.nlist.Cell(buffer=self.buffer)
        cell.rebuild_check_delay = self.rebuild_check_delay

        sim = hoomd.Simulation(device=self.device)
        sim.create_state_from_gsd(filename=str(path))
        sim.always_compute_pressure = self.always_compute_pressure

        if self.pair_class is hoomd.md.pair.LJ:
            pair = self.pair_class(nlist=cell,
                                   tail_correction=self.tail_correction)
        else:
            pair = self.pair_class(nlist=cell)

        particle_types = sim.state.particle_types
        pair.params[(particle_types, particle_types)] = self.pair_params
        pair.r_cut[(particle_types, particle_types)] = self.r_cut
        if hasattr(pair, 'r_on'):
            pair.r_on[(particle_types, particle_types)] = self.r_cut * 0.9
        pair.mode = self.mode
        integrator.forces.append(pair)
        nvt = hoomd.md.methods.NVT(kT=1.2, filter=hoomd.filter.All(), tau=0.5)
        integrator.methods.append(nvt)

        sim.operations.integrator = integrator

        return sim
