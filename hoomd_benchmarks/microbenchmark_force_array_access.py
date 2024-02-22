# Copyright (c) 2021-2024 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Force array access benchmark."""

import hoomd

from . import common
from .configuration.hard_sphere import make_hard_sphere_configuration
from .microbenchmark_custom_force import ConstantForce


class AccessForceAction(hoomd.custom.Action):
    """An action to access the per-particle force arrays."""

    def __init__(self, force=None):
        self._force = force

    def act(self, timestep):
        """Access the forces arrays but do nothing with them."""
        if self._force is None:
            return
        forces = self._force.forces  # noqa: F841
        energies = self._force.energies  # noqa: F841
        torques = self._force.torques  # noqa: F841
        virials = self._force.virials  # noqa: F841


class MicrobenchmarkForceArrayAccess(common.ComparativeBenchmark):
    """Measure the overhead of accessing the force arrays.

    Add an AccessForceAction object to both simulations, but only populate one
    of them with a Force object. Then the only difference in the performance
    between the two simulations will caused by accessing the arrays associated
    with the Force object.
    """

    SUITE_STEP_SCALE = 0.01

    def make_simulations(self):
        """Make the simulation objects."""
        path = make_hard_sphere_configuration(
            N=self.N,
            rho=self.rho,
            dimensions=self.dimensions,
            device=self.device,
            verbose=self.verbose,
        )

        dt = 0.0
        sim0 = hoomd.Simulation(device=self.device, seed=100)
        sim0.create_state_from_gsd(filename=str(path))
        sim0.operations.updaters.clear()
        sim0.operations.computes.clear()
        sim0.operations.writers.clear()
        sim0.operations.tuners.clear()
        sim0.operations.integrator = hoomd.md.Integrator(
            dt=dt,
            methods=[hoomd.md.methods.ConstantVolume(filter=hoomd.filter.All())],
        )
        constant_custom_force_sim0 = ConstantForce(5, sim0.device)
        sim0.operations.integrator.forces.append(constant_custom_force_sim0)
        # don't add force to writer in sim0
        sim0.operations.add(hoomd.write.CustomWriter(1, AccessForceAction()))

        sim1 = hoomd.Simulation(device=self.device, seed=100)
        sim1.create_state_from_gsd(filename=str(path))
        sim1.operations.updaters.clear()
        sim1.operations.computes.clear()
        sim1.operations.writers.clear()
        sim1.operations.tuners.clear()
        sim1.operations.integrator = hoomd.md.Integrator(
            dt=dt,
            methods=[hoomd.md.methods.ConstantVolume(filter=hoomd.filter.All())],
        )
        constant_custom_force_sim1 = ConstantForce(5, sim1.device)
        sim1.operations.integrator.forces.append(constant_custom_force_sim1)
        # do add force to writer in sim1
        sim1.operations.add(
            hoomd.write.CustomWriter(1, AccessForceAction(constant_custom_force_sim1))
        )

        return sim0, sim1


if __name__ == '__main__':
    MicrobenchmarkForceArrayAccess.main()
