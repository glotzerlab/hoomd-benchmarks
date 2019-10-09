import flow
from flow import environments
from flow import FlowProject
import signac
import numpy as np
import math

class Project(FlowProject):
    pass

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

            # read the initial config or restart file
            system = hoomd.init.read_gsd(filename=signac.get_project().fn('init.gsd'))

            # setup the MC integration
            mc = hpmc.integrate.convex_polygon(seed=20, d=0.17010672166874857, a=1.0471975511965976, nselect=4);
            mc.shape_param.set('A', vertices=[[0.5,0],[0.25,0.433012701892219],[-0.25,0.433012701892219],[-0.5,0],[-0.25,-0.433012701892219],[0.25,-0.433012701892219]]);

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

if __name__ == '__main__':
    project = signac.get_project()

    for conf in project.doc['exec_confs']:
        add_benchmark(mode=conf['mode'], gpu_ids=conf['gpu_ids'], nranks=conf['nranks'])
    Project().main()

