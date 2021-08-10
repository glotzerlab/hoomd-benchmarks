"""Hard sphere initial configuration."""

import hoomd
import pathlib
import numpy
import math
import itertools


def make_hard_sphere_configuration(N, rho, dimensions, device, verbose):
    """Make an initial configuration of hard spheres, or find it in the cache.

    Args:
        N (int): Number of particles.
        rho (float): Number density.
        dimensions (int): Number of dimensions (2 or 3).
        device (hoomd.device.Device): Device object to execute on.
        verbose (bool): Set to True to provide details to stdout.

    Initialize a system of N randomly placed hard spheres at the given number
    density *phi* and diameter 1.0.
    """
    filename = f'hard_sphere_{N}_{rho}_{dimensions}.gsd'
    file_path = pathlib.Path('initial_configuration_cache') / filename

    print_messages = verbose and device.communicator.rank == 0

    if dimensions != 2 and dimensions != 3:
        raise ValueError('Invalid dimensions: must be 2 or 3')

    if file_path.exists():
        if print_messages:
            print(f'Using existing {file_path}')
        return file_path

    if print_messages:
        print(f'Generating {file_path}')

    # initial configuration on a grid
    spacing = 1.5
    K = math.ceil(N**(1 / dimensions))
    L = K * spacing

    snapshot = hoomd.Snapshot(communicator=device.communicator)
    if dimensions == 3:
        snapshot.configuration.box = [L, L, L, 0, 0, 0]
    else:
        snapshot.configuration.box = [L, L, 0, 0, 0, 0]

    if snapshot.communicator.rank == 0:
        snapshot.particles.types = ['A']
        snapshot.particles.N = N
        x = numpy.linspace(-L / 2, L / 2, K, endpoint=False)
        position_grid = list(itertools.product(x, repeat=dimensions))
        snapshot.particles.position[:, 0:dimensions] = position_grid[0:N]

    # randomize the system
    mc = hoomd.hpmc.integrate.Sphere()
    mc.shape['A'] = dict(diameter=1.0)

    sim = hoomd.Simulation(device=device, seed=10)
    sim.create_state_from_snapshot(snapshot)
    sim.operations.integrator = mc

    if print_messages:
        print('.. randomizing positions')

    for i in range(5):
        sim.run(1000)
        if print_messages:
            print(f'.. step {sim.timestep} at {sim.tps:0.4g} TPS')

    # compress to the target density
    initial_box = sim.state.box
    final_box = hoomd.Box.from_box(initial_box)
    final_box.volume = N / rho
    periodic = hoomd.trigger.Periodic(10)
    compress = hoomd.hpmc.update.QuickCompress(trigger=periodic,
                                               target_box=final_box)
    sim.operations.updaters.append(compress)

    tune = hoomd.hpmc.tune.MoveSize.scale_solver(moves=['d'],
                                                 target=0.2,
                                                 trigger=periodic,
                                                 max_translation_move=0.2)
    sim.operations.tuners.append(tune)

    if print_messages:
        print('.. compressing')
    while not compress.complete and sim.timestep < 1e6:
        sim.run(500)
        if print_messages:
            print(f'.. step {sim.timestep} at {sim.tps:0.4g} TPS')

    if not compress.complete:
        raise RuntimeError('Compression failed to complete')

    hoomd.write.GSD.write(state=sim.state, mode='xb', filename=str(file_path))

    if print_messages:
        print('.. done')
    return file_path
