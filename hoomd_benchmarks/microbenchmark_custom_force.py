# Copyright (c) 2021-2023 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Custom Force benchmark."""

import warnings

import hoomd
import numpy as np

from . import common
from .configuration.hard_sphere import make_hard_sphere_configuration

try:
    import cupy as cp

    CUPY_IMPORTED = True
except ImportError:
    CUPY_IMPORTED = False


class ConstantForce(hoomd.md.force.Custom):
    """Custom force which implements the force of gravity."""

    def __init__(self, magnitude, device):
        super().__init__()
        self._mag = magnitude
        self._device = device
        device_str = device.__class__.__name__.lower()
        self._local_force_str = device_str + '_local_force_arrays'
        self._local_snapshot_str = device_str + '_local_snapshot'

    def _to_array(self, list_data):
        if isinstance(self._device, hoomd.device.CPU) or not CUPY_IMPORTED:
            return np.array(list_data)

        return cp.array(list_data)

    def set_forces(self, timestep):
        """Set the forces."""
        # handle the case where cupy is not imported on the GPU
        if not CUPY_IMPORTED and isinstance(self._device, hoomd.device.GPU):
            return

        with getattr(self, self._local_force_str) as arrays, getattr(
            self._state, self._local_snapshot_str
        ) as snap:
            arrays.force[:] = self._to_array([0, 0, -self._mag])
            arrays.potential_energy[:] = (
                self._to_array(snap.particles.position[:, 2]) * self._mag
            )


class MicrobenchmarkCustomForce(common.ComparativeBenchmark):
    """Measure the overhead of a constant custom force.

    This benchmark performs an
    """

    def execute(self):
        """Override execute to skip this benchamrk without cupy installed."""
        if isinstance(self.device, hoomd.device.CPU) or CUPY_IMPORTED:
            return super().execute()

        warnings.warn(
            'Skipping microbenchmark_custom_force on GPU device '
            ' - cupy is not available.',
            stacklevel=2,
        )
        return [0]

    def make_simulations(self):
        """Make the simulation objects."""
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
            dt=0.001,
            methods=[hoomd.md.methods.ConstantVolume(filter=hoomd.filter.All())],
        )

        sim1 = hoomd.Simulation(device=self.device, seed=100)
        sim1.create_state_from_gsd(filename=str(path))
        sim1.operations.updaters.clear()
        sim1.operations.computes.clear()
        sim1.operations.writers.clear()
        sim1.operations.tuners.clear()
        sim1.operations.integrator = hoomd.md.Integrator(
            dt=0.001,
            methods=[hoomd.md.methods.ConstantVolume(filter=hoomd.filter.All())],
        )

        constant_custom_force = ConstantForce(5, sim1.device)
        sim1.operations.integrator.forces.append(constant_custom_force)

        return sim0, sim1

    @classmethod
    def runs_on_device(cls, device):
        """Returns True when the benchmark can be run on the given device."""
        if isinstance(device, hoomd.device.GPU) and not CUPY_IMPORTED:
            # cupy is required to run this device on the GPU
            return False

        return True


if __name__ == '__main__':
    MicrobenchmarkCustomForce.main()
