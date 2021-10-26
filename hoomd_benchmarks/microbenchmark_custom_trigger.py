# Copyright (c) 2021 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Hard sphere Monte Carlo benchmark."""

import hoomd
from . import common
from .configuration.hard_sphere import make_hard_sphere_configuration


class NeverTrigger(hoomd.trigger.Trigger):
    """A trigger that always returns False."""

    def __init__(self):
        hoomd.trigger.Trigger.__init__(self)

    def compute(self, timestep):
        """Compute the value of the trigger."""
        return False


class MicrobenchmarkCustomTrigger(common.Benchmark):
    """Measure the overhead of evaluating a custom trigger.

    See Also:
        `common.Benchmark`
    """

    def make_simulations(self):
        """Make the Simulation object."""
        path = make_hard_sphere_configuration(N=self.N,
                                              rho=self.rho,
                                              dimensions=self.dimensions,
                                              device=self.device,
                                              verbose=self.verbose)

        variant = hoomd.variant.Ramp(A=0, B=1, t_start=0, t_ramp=100)

        sim0 = hoomd.Simulation(device=self.device, seed=100)
        sim0.create_state_from_gsd(filename=str(path))
        sim0.operations.updaters.clear()
        sim0.operations.computes.clear()
        sim0.operations.writers.clear()
        sim0.operations.tuners.clear()

        trigger0 = hoomd.trigger.Periodic(phase=1000000000, period=1000000000)
        box = sim0.state.box
        box_resize1 = hoomd.update.BoxResize(trigger=trigger0,
                                             box1=box,
                                             box2=box,
                                             variant=variant,
                                             filter=hoomd.filter.All())
        sim0.operations.updaters.append(box_resize1)

        sim1 = hoomd.Simulation(device=self.device, seed=100)
        sim1.create_state_from_gsd(filename=str(path))
        sim1.operations.updaters.clear()
        sim1.operations.computes.clear()
        sim1.operations.writers.clear()
        sim1.operations.tuners.clear()

        trigger1 = NeverTrigger()
        box = sim1.state.box
        box_resize1 = hoomd.update.BoxResize(trigger=trigger1,
                                             box1=box,
                                             box2=box,
                                             variant=variant,
                                             filter=hoomd.filter.All())
        sim1.operations.updaters.append(box_resize1)

        self.units = 'nanoseconds per step'

        return [sim0, sim1]

    def get_performance(self):
        """Get the benchmark performance."""
        t0 = 1 / self.simulations[0].tps / 1e-9
        t1 = 1 / self.simulations[1].tps / 1e-9
        return t1 - t0


if __name__ == '__main__':
    MicrobenchmarkCustomTrigger.main()
