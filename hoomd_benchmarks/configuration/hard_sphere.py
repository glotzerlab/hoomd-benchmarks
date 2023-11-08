# Copyright (c) 2021-2023 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Hard sphere initial configuration."""

import itertools
import math
import pathlib

import gsd.hoomd
import hoomd
import numpy


def make_hard_sphere_configuration(N,
                                   rho,
                                   dimensions,
                                   device,
                                   verbose,
                                   n_types=1):
    """Make an initial configuration of hard spheres, or find it in the cache.

    Args:
        N (int): Number of particles.
        rho (float): Number density.
        dimensions (int): Number of dimensions (2 or 3).
        device (hoomd.device.Device): Device object to execute on.
        verbose (bool): Set to True to provide details to stdout.
        n_types (int): Number of particle types.

    Initialize a system of N randomly placed hard spheres at the given number
    density *phi* and diameter 1.0.

    When ``n_types`` is 1, the particle type is 'A'. When ``n_types`` is greater
    than 1, the types are assigned sequentially to particles and named
    ``str(type_id)``.
    """
    print_messages = verbose and device.communicator.rank == 0

    if n_types > 1:
        one_type_path = make_hard_sphere_configuration(N, rho, dimensions,
                                                       device, verbose, 1)

        filename = f'hard_sphere_{N}_{rho}_{dimensions}_{n_types}.gsd'
        file_path = pathlib.Path('initial_configuration_cache') / filename

        if print_messages:
            print(f'.. adding types to {file_path}')

        # add types to the file
        if device.communicator.rank == 0:
            with gsd.hoomd.open(one_type_path, mode='rb') as one_type_gsd:
                snapshot = one_type_gsd[0]
                snapshot.particles.types = [str(i) for i in range(0, n_types)]
                snapshot.particles.typeid = [
                    i % n_types for i in range(0, snapshot.particles.N)
                ]

                with gsd.hoomd.open(file_path, mode='wb') as n_types_gsd:
                    n_types_gsd.append(snapshot)

        return file_path

    filename = f'hard_sphere_{N}_{rho}_{dimensions}.gsd'
    file_path = pathlib.Path('initial_configuration_cache') / filename

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

    for i in range(10):
        sim.run(100)
        tps = sim.tps
        if print_messages:
            print(f'.. step {sim.timestep} at {tps:0.4g} TPS')

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
    while not compress.complete and sim.timestep < 1e5:
        sim.run(100)
        tps = sim.tps
        box = sim.state.box
        if print_messages:
            progress = (math.fabs(initial_box.volume - box.volume)
                        / math.fabs(initial_box.volume - final_box.volume))
            print(f'.. step {sim.timestep} at {tps:0.4g} TPS: '
                  f'progress {progress*100:0.4g}%')

    if not compress.complete:
        raise RuntimeError('Compression failed to complete')

    hoomd.write.GSD.write(state=sim.state, mode='xb', filename=str(file_path))

    if print_messages:
        print('.. done')
    return file_path
