"""Hard sphere Monte Carlo benchmark."""

import hoomd
import numpy
from . import common
from .configuration.hard_sphere import make_hard_sphere_configuration

DEFAULT_N = 64000
DEFAULT_RHO = 1.0
DEFAULT_DIMENSIONS = 3


def benchmark(device,
              N=DEFAULT_N,
              rho=DEFAULT_RHO,
              dimensions=DEFAULT_DIMENSIONS,
              **kwargs):
    """Run the hard sphere Monte Carlo benchmark.

    Args:
        device (hoomd.device.Device): Device object to execute on.
        N (int): The number of particles.
        rho (float): The number density.
        dimensions (int): The number of dimensions (2 or 3).

        kwargs (dict): Capture other command line arguments in order to pass
          them to `common.run_simulation_benchmark`.

    Returns:
        list[float]: The performance in time steps per second measured at each
            benchmark stage.
    """
    kwargs = common.update_common_defaults(kwargs)

    path = make_hard_sphere_configuration(N=N,
                                          rho=rho,
                                          dimensions=dimensions,
                                          device=device,
                                          verbose=kwargs['verbose'])

    if kwargs['verbose'] and device.communicator.rank == 0:
        print('Running hard sphere Monte Carlo benchmark')

    mc = hoomd.hpmc.integrate.Sphere()
    mc.shape['A'] = dict(diameter=1.0)

    sim = hoomd.Simulation(device=device, seed=100)
    sim.create_state_from_gsd(filename=str(path))
    sim.operations.integrator = mc

    def get_performance(sim):
        mc = sim.operations.integrator
        return ((sum(mc.translate_moves) + sum(mc.rotate_moves)) / sim.walltime
                / sim.state.N_particles)

    return common.run_simulation_benchmark(sim=sim,
                                           get_performance=get_performance,
                                           units="trial moves per second "
                                           "per particle",
                                           **kwargs)


if __name__ == '__main__':
    parser = common.make_common_argument_parser()
    parser.add_argument('-N',
                        type=int,
                        default=DEFAULT_N,
                        help='Number of particles.')
    parser.add_argument('--rho',
                        type=float,
                        default=DEFAULT_RHO,
                        help='Number density.')
    parser.add_argument('--dimensions',
                        type=int,
                        choices=[2, 3],
                        help='Number of dimensions.',
                        default=DEFAULT_DIMENSIONS)
    args = parser.parse_args()
    args.device = common.make_hoomd_device(args)
    performance = benchmark(**vars(args))

    if args.device.communicator.rank == 0:
        print(f'{numpy.mean(performance)}')
