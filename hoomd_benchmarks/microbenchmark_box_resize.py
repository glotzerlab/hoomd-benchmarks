# Copyright (c) 2021-2024 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Box resize benchmark."""

import hoomd

from . import common
from .configuration.hard_sphere import make_hard_sphere_configuration


class MicrobenchmarkBoxResize(common.Benchmark):
    """Measure the performance of the box resize updater.

    See Also:
        `common.Benchmark`
    """

    def make_simulation(self):
        """Make the Simulation object."""
        path = make_hard_sphere_configuration(
            N=self.N,
            rho=self.rho,
            dimensions=self.dimensions,
            device=self.device,
            verbose=self.verbose,
        )

        sim = hoomd.Simulation(device=self.device, seed=100)
        sim.create_state_from_gsd(filename=str(path))
        sim.operations.updaters.clear()
        sim.operations.computes.clear()
        sim.operations.writers.clear()
        sim.operations.tuners.clear()

        box_resize_trigger = hoomd.trigger.Periodic(1)
        initial_box = sim.state.box
        final_box = hoomd.Box.from_box(initial_box)
        final_box.volume = initial_box.volume / 2

        ramp = hoomd.variant.Ramp(
            A=0,
            B=1,
            t_start=sim.timestep,
            t_ramp=self.warmup_steps * 10 + self.repeat * self.benchmark_steps,
        )
        box_resize = hoomd.update.BoxResize(
            box1=initial_box, box2=final_box, variant=ramp, trigger=box_resize_trigger
        )
        sim.operations.updaters.append(box_resize)

        return sim


if __name__ == '__main__':
    MicrobenchmarkBoxResize.main()
