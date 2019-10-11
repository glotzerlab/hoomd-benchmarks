import flow
from flow import environments
from flow import FlowProject
import signac
import numpy as np
import math


benchmark_name = 'dodecahedron'

# dodecahedron shape
phi = (1. + math.sqrt(5.))/2.
inv = 2./(1. + math.sqrt(5.))
points = [
          (-1,-1,-1),
          (-1,-1, 1),
          (-1, 1,-1),
          (-1, 1, 1),
          ( 1,-1,-1),
          ( 1,-1, 1),
          ( 1, 1,-1),
          ( 1, 1, 1),
          ( 0,-inv,-phi),
          ( 0,-inv, phi),
          ( 0, inv,-phi),
          ( 0, inv, phi),
          (-inv,-phi, 0),
          (-inv, phi, 0),
          ( inv,-phi, 0),
          ( inv, phi, 0),
          (-phi, 0,-inv),
          (-phi, 0, inv),
          ( phi, 0,-inv),
          ( phi, 0, inv)
         ]

V = 14.4721 # Mathematica
circ_r = np.max(np.linalg.norm(np.array(points), axis=1))

@FlowProject.label
def pertains(job):
    global benchmark_name
    return job.statepoint()['benchmark'] == benchmark_name

@FlowProject.label
def compressed(job):
    return job.isfile('init.gsd')

# factory method
def add_compression(project):
    @project.operation('{}-compress'.format(benchmark_name))
    @project.pre(pertains)
    @project.post(compressed)
    def compress(job):
        sp = job.statepoint()

        with job:
            import hoomd
            from hoomd import hpmc

            c = hoomd.context.initialize()
            phi_p_ini = 0.2
            phi_p_target = 0.5
            n = sp['n']
            L_target = n*(V/phi_p_target)**(1./3.)

            system = hoomd.init.create_lattice(n=n, unitcell=hoomd.lattice.sc(a=(V/phi_p_ini)**(1./3.)))

            # setup the MC integration
            mc = hpmc.integrate.convex_polyhedron(seed=10, d=0.3, a=0.26);
            mc.shape_param.set("A", vertices=points);

            hoomd.run(1,quiet=True)

            # shrink the box to the target
            scale = 0.99
            L = system.box.Lx
            while L_target < L:
                # shrink the box
                L = max(L*scale, L_target);

                hoomd.update.box_resize(Lx=L, Ly=L, Lz=L, period=None);
                overlaps = mc.count_overlaps();
                if c.device.comm.rank == 0:
                    print("phi = {:.3f}: overlaps = {} ".format(((n*n*n*V) / (L*L*L)), overlaps), end = '');

                # run until all overlaps are removed
                while overlaps > 0:
                    #mc_tune.update()
                    hoomd.run(100, quiet=True);
                    overlaps = mc.count_overlaps();
                    if c.device.comm.rank == 0:
                        print('{}'.format(overlaps),end='')

                if c.device.comm.rank == 0:
                    print('')

            # thermalize
            hoomd.run(10000)
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

    @project.operation('{}-benchmark-{}'.format(benchmark_name,name))
    @project.pre(pertains)
    @project.pre(compressed)
    @flow.directives(nranks=nranks)
    @flow.directives(np=nranks)
    @flow.directives(ngpu=ngpu)
    def benchmark(job):
        sp = job.statepoint()

        with job:
            import hoomd
            from hoomd import hpmc

            device = hoomd.device.GPU(gpu_ids=gpu_ids) if mode == 'gpu' else hoomd.device.CPU()
            c = hoomd.context.initialize(device)
            system = hoomd.init.read_gsd(filename=job.fn('init.gsd'))

            # setup the MC integration
            mc = hpmc.integrate.convex_polyhedron(seed=10, d=0.3, a=0.26);
            mc.shape_param.set("A", vertices=points);

            # warm up and autotune
            if c.device.mode == 'gpu':
                hoomd.run(1000)
            else:
                hoomd.run(1000, limit_hours=20.0/3600.0)

            # full benchmark
            tps = hoomd.benchmark.series(warmup=0, repeat=4, steps=50000, limit_hours=20.0/3600.0)

            # correct get_mps based on average of TPS values (get_mps is only for the last run())
            mps = mc.get_mps() / tps[-1] * np.mean(tps);

            # print out millions of particle time steps per second
            if c.device.comm.rank == 0:
                print("Hours to complete 10e6 steps: {0}".format(10e6/(mps/len(system.particles))/3600));
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
                row['mps'] = mps
                row['tps'] = tps

                job.doc[name] = row
