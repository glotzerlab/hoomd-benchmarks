"""Methods common to MD pair potential benchmarks."""

import hoomd
import numpy
from . import common
from .configuration.hard_sphere import make_hard_sphere_configuration

DEFAULT_N = 64000
DEFAULT_RHO = 1.0
DEFAULT_DIMENSIONS = 3


def main(pair_class, pair_params, r_cut):
    """Implement the main entrypoint for all MD pair potential benchmarks."""
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
    performance = benchmark(**vars(args),
                            pair_class=pair_class,
                            pair_params=pair_params,
                            r_cut=r_cut)

    if args.device.communicator.rank == 0:
        print(f'{numpy.mean(performance)}')


def benchmark(device,
              pair_class,
              pair_params,
              r_cut,
              N=DEFAULT_N,
              rho=DEFAULT_RHO,
              dimensions=DEFAULT_DIMENSIONS,
              **kwargs):
    """Run the pair potential benchmark.

    Args:
        device (hoomd.device.Device): Device object to execute on.
        pair_class (hoomd.md.pair.Pair): Pair force class to use.
        pair_params (dict): Pair potential parameters.
        r_cut (float): Cutoff radius.
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
        print('Running Lennard-Jones pair potential benchmark')

    integrator = hoomd.md.Integrator(dt=0.005)
    cell = hoomd.md.nlist.Cell()
    pair = pair_class(nlist=cell)
    pair.params[('A', 'A')] = pair_params
    pair.r_cut[('A', 'A')] = r_cut
    integrator.forces.append(pair)
    nvt = hoomd.md.methods.NVT(kT=1.2, filter=hoomd.filter.All(), tau=0.5)
    integrator.methods.append(nvt)

    sim = hoomd.Simulation(device=device)
    sim.create_state_from_gsd(filename=str(path))
    sim.operations.integrator = integrator

    return common.run_simulation_benchmark(sim=sim,
                                           get_performance=lambda sim: sim.tps,
                                           **kwargs)
