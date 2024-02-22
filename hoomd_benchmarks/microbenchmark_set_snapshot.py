# Copyright (c) 2021-2024 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""set_snapshot benchmark."""

import hoomd

from . import common
from .configuration.hard_sphere import make_hard_sphere_configuration
from .microbenchmark_custom_updater import EmptyAction


class SetSnapshotAction(hoomd.custom.Action):
    """Action that sets the system snapshot."""

    def __init__(self, snapshot):
        self.snap = snapshot

    def act(self, timestep):
        """Set the system snapshot."""
        self._state.set_snapshot(self.snap)


class MicrobenchmarkSetSnapshot(common.ComparativeBenchmark):
    """Measure the overhead of setting a global snapshot.

    This benchmark performs an MD integration with no forces and dt=0 to ensure
    that the particle data is moved to the GPU every timestep before it calls
    set_snapshot.

    See Also:
        `common.ComparativeBenchmark`
    """

    SUITE_STEP_SCALE = 0.01

    def make_simulations(self):
        """Make the Simulation objects."""
        path = make_hard_sphere_configuration(
            N=self.N,
            rho=self.rho,
            dimensions=self.dimensions,
            device=self.device,
            verbose=self.verbose,
        )

        sim0 = hoomd.Simulation(device=self.device, seed=100)
        sim0.create_state_from_gsd(filename=str(path))
        sim0.operations.updaters.clear()
        sim0.operations.computes.clear()
        sim0.operations.writers.clear()
        sim0.operations.tuners.clear()
        sim0.operations.integrator = hoomd.md.Integrator(
            dt=0.0, methods=[hoomd.md.methods.ConstantVolume(filter=hoomd.filter.All())]
        )

        empty_updater = hoomd.update.CustomUpdater(
            action=EmptyAction(), trigger=hoomd.trigger.Periodic(period=1)
        )
        sim0.operations.updaters.append(empty_updater)

        sim1 = hoomd.Simulation(device=self.device, seed=100)
        sim1.create_state_from_gsd(filename=str(path))
        sim1.operations.updaters.clear()
        sim1.operations.computes.clear()
        sim1.operations.writers.clear()
        sim1.operations.tuners.clear()
        sim1.operations.integrator = hoomd.md.Integrator(
            dt=0.0, methods=[hoomd.md.methods.ConstantVolume(filter=hoomd.filter.All())]
        )

        set_snapshot_updater = hoomd.update.CustomUpdater(
            action=SetSnapshotAction(sim1.state.get_snapshot()),
            trigger=hoomd.trigger.Periodic(period=1),
        )
        sim1.operations.updaters.append(set_snapshot_updater)

        return sim0, sim1


if __name__ == '__main__':
    MicrobenchmarkSetSnapshot.main()
