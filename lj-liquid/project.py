import flow
from flow import environments
from flow import FlowProject
import signac
import numpy as np
import math

class Project(FlowProject):
    pass

@FlowProject.label
def equilibrated(job):
    return job.isfile('init.gsd')

@Project.operation
@Project.post(equilibrated)
def equilibrate(job):
    sp = job.statepoint()

    with job:
        import hoomd
        from hoomd import md

        hoomd.context.initialize()
        phi_p = 0.2
        system = hoomd.init.create_lattice(n=sp['n'], unitcell=hoomd.lattice.sc(a=((math.pi/6)/phi_p)**(1./3.)))

        nl = md.nlist.cell()
        lj = md.pair.lj(r_cut=3.0,nlist=nl)
        lj.pair_coeff.set('A', 'A', epsilon=1.0, sigma=1.0)

        md.integrate.mode_standard(dt=0.005)
        nvt = md.integrate.nvt(group=hoomd.group.all(), kT=1.2, tau=0.5)
        nvt.randomize_velocities(seed=42)

        hoomd.run(200000)
        hoomd.dump.gsd('init.gsd', period=None, overwrite=True,group=hoomd.group.all())

def add_benchmark(mode, nranks, gpu_ids=[]):
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
    name += '_nranks{}'.format(nranks)

    @Project.operation('bmark-{}'.format(name))
    @Project.pre(equilibrated)
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
            nl = md.nlist.cell()
            lj = md.pair.lj(r_cut=3.0, nlist=nl)
            lj.pair_coeff.set('A', 'A', epsilon=1.0, sigma=1.0)

            md.integrate.mode_standard(dt=0.005)
            md.integrate.nvt(group=hoomd.group.all(), kT=1.2, tau=0.5)

            nl.set_params(r_buff=0.6, check_period=7)

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

if __name__ == '__main__':
    project = signac.get_project()

    for conf in project.doc['exec_confs']:
        add_benchmark(mode=conf['mode'], gpu_ids=conf['gpu_ids'], nranks=conf['nranks'])
    Project().main()

