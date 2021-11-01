# Copyright (c) 2021 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Custom Updater benchmark."""

import hoomd
from . import common
from .configuration.hard_sphere import make_hard_sphere_configuration


class EmptyAction(hoomd.custom.Action):
    """Action that does nothing."""

    def act(self, timestep):
        """Do nothing."""
        return


class MicrobenchmarkCustomUpdater(common.ComparativeBenchmark):
    """Measure the overhead of evaluating a custom updater.

    See Also:
        `common.ComparativeBenchmark`
    """

    def make_simulations(self):
        """Make the Simulation objects."""
        path = make_hard_sphere_configuration(N=self.N,
                                              rho=self.rho,
                                              dimensions=self.dimensions,
                                              device=self.device,
                                              verbose=self.verbose)

        sim0 = hoomd.Simulation(device=self.device, seed=100)
        sim0.create_state_from_gsd(filename=str(path))
        sim0.operations.updaters.clear()
        sim0.operations.computes.clear()
        sim0.operations.writers.clear()
        sim0.operations.tuners.clear()

        sim1 = hoomd.Simulation(device=self.device, seed=100)
        sim1.create_state_from_gsd(filename=str(path))
        sim1.operations.updaters.clear()
        sim1.operations.computes.clear()
        sim1.operations.writers.clear()
        sim1.operations.tuners.clear()

        custom_updater = hoomd.update.CustomUpdater(
            action=EmptyAction(), trigger=hoomd.trigger.Periodic(period=1))
        sim1.operations.updaters.append(custom_updater)

        return sim0, sim1


if __name__ == '__main__':
    MicrobenchmarkCustomUpdater.main()
