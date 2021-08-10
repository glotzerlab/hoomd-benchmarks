"""Methods common to MD pair potential benchmarks."""

import hoomd
from . import common
from .configuration.hard_sphere import make_hard_sphere_configuration


class MDPair(common.Benchmark):
    """Base class pair potential benchmark.

    Derived classes should set the class level variables ``pair_class``,
    ``pair_params``, and ``r_cut``.

    See Also:
        `common.Benchmark`
    """

    def make_simulation(self):
        """Make the Simulation object."""
        path = make_hard_sphere_configuration(N=self.N,
                                              rho=self.rho,
                                              dimensions=self.dimensions,
                                              device=self.device,
                                              verbose=self.verbose)

        integrator = hoomd.md.Integrator(dt=0.005)
        cell = hoomd.md.nlist.Cell()
        pair = self.pair_class(nlist=cell)
        pair.params[('A', 'A')] = self.pair_params
        pair.r_cut[('A', 'A')] = self.r_cut
        integrator.forces.append(pair)
        nvt = hoomd.md.methods.NVT(kT=1.2, filter=hoomd.filter.All(), tau=0.5)
        integrator.methods.append(nvt)

        sim = hoomd.Simulation(device=self.device)
        sim.create_state_from_gsd(filename=str(path))
        sim.operations.integrator = integrator

        return sim
