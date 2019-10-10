import flow
from flow import environments
from flow import FlowProject
import signac
import numpy as np
import math

benchmark_name = 'quasicrystal'

potential_k    = 6.25
potential_phi  = 0.62
temperature    = 180 * 0.001

# Definition of EOPP potential
def EOPP(r, rmin, rmax, k, phi):
    cos = math.cos(k * (r - 1.25) - phi)
    sin = math.sin(k * (r - 1.25) - phi)
    V =        pow(r, -15) +       cos * pow(r, -3)
    F = 15.0 * pow(r, -16) + 3.0 * cos * pow(r, -4) + k * sin * pow(r, -3)
    return (V, F)

# Determine the cut-off by searching for extrema
def determineCutoff(k, phi):
    r = 0.5
    extremaNum = 0
    force1 = EOPP(r, 0, 0, k, phi)[1]
    while (extremaNum < 6 and r < 5.0):
        r += 0.00001
        force2 = EOPP(r, 0, 0, k, phi)[1]
        if (force1 * force2 < 0.0):
            extremaNum += 1
        force1 = force2
    return r

@FlowProject.label
def pertains(job):
    global benchmark_name
    return job.statepoint()['benchmark'] == benchmark_name

@FlowProject.label
def equilibrated(job):
    return job.isfile('init.gsd')

# factory method
def add_equilibration(project):
    @project.operation('{}-equilibrate'.format(benchmark_name))
    @project.pre(pertains)
    @project.post(equilibrated)
    def equilibrate(job):
        sp = job.statepoint()

        with job:
            import hoomd
            from hoomd import md

            hoomd.context.initialize()
            rho = 0.03
            system = hoomd.init.create_lattice(n=sp['n'], unitcell=hoomd.lattice.sc(a=rho**(-1./3.)))

            # generate the pair interaction table
            cutoff = determineCutoff(potential_k, potential_phi)
            nl = md.nlist.cell()
            table = md.pair.table(nlist = nl, width = 1000)
            table.pair_coeff.set('A', 'A', func = EOPP, rmin = 0.5, rmax = cutoff,
                                 coeff = dict(k = potential_k, phi = potential_phi))

            # Integrate at constant temperature
            md.integrate.nvt(group = hoomd.group.all(), tau = 1.0, kT = temperature)
            md.integrate.mode_standard(dt = 0.01)

            hoomd.run(100000)
            hoomd.dump.gsd('init.gsd', period=None, overwrite=True,group=hoomd.group.all())

def add_benchmark(project, mode, nranks, gpu_ids=[]):
    name = ''
    ngpu = 0
    if mode == 'cpu':
        name += 'cpu'
    elif mode == 'gpu':
        name += 'gpu'
        ngpu = max(1,len(gpu_ids))
        ngpu *= nranks
    else:
        raise ValueError('Unknown execution mode')

    name += '_'.join([str(g) for g in gpu_ids])
    name += '_np{}'.format(nranks)

    @project.operation('{}-benchmark-{}'.format(benchmark_name, name))
    @project.pre(equilibrated)
    @project.pre(pertains)
    @flow.directives(nranks=nranks)
    @flow.directives(np=nranks)
    @flow.directives(ngpu=ngpu)
    def benchmark(job):
        sp = job.statepoint()

        with job:
            import hoomd
            from hoomd import md

            device = hoomd.device.GPU(gpu_ids=gpu_ids) if mode == 'gpu' else hoomd.device.CPU()
            c = hoomd.context.initialize(device)
            system = hoomd.init.read_gsd(filename=job.fn('init.gsd'))

            # generate the pair interaction table
            cutoff = determineCutoff(potential_k, potential_phi)
            nl = md.nlist.cell()
            table = md.pair.table(nlist = nl, width = 1000)
            table.pair_coeff.set('A', 'A', func = EOPP, rmin = 0.5, rmax = cutoff,
                                 coeff = dict(k = potential_k, phi = potential_phi))

            # Integrate at constant temperature
            md.integrate.nvt(group = hoomd.group.all(), tau = 1.0, kT = temperature)
            md.integrate.mode_standard(dt = 0.01)

            nl.set_params(r_buff=0.35, check_period=4)

            # warm up and autotune
            if c.device.mode == 'gpu':
                hoomd.run(30000)
            else:
                hoomd.run(30000, limit_hours=20.0/3600.0)

            # full benchmark
            tps = hoomd.benchmark.series(warmup=0, repeat=4, steps=50000, limit_hours=20.0/3600.0)
            ptps = np.average(tps) * len(system.particles);

            # print out millions of particle time steps per second
            if c.device.comm.rank == 0:
                print("Hours to complete 10e6 steps: {0}".format(10e6/(ptps/len(system.particles))/3600));
                row = dict()

                # meta data
                meta = hoomd.meta.dump_metadata()
                row['N'] = meta['hoomd.data.system_data']['particles']['N'];
                row['num_ranks'] = meta['device']['num_ranks'];
                row['compiler_version'] = meta['hoomd']['compiler_version'];
                row['cuda_version'] = meta['hoomd']['cuda_version'];
                row['hoomd_version'] = meta['hoomd']['hoomd_version'];
                row['gpu'] = meta['device']['gpu_ids'];
                row['mode'] = meta['device']['mode'];

                compile_flags = meta['hoomd']['hoomd_compile_flags'].split();
                row['precision'] = 'n/a'
                if 'SINGLE' in compile_flags:
                    row['precision'] = 'single';
                if 'DOUBLE' in compile_flags:
                    row['precision'] = 'double';

                # benchmark performance
                row['mps'] = ptps
                row['tps'] = tps

                job.doc[name] = row
