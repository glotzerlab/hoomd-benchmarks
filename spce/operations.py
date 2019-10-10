import flow
from flow import environments
from flow import FlowProject
import signac
import numpy as np
import math

benchmark_name = 'spce'

density = 994 # kg m^-3
T_kelvin = 300 #K

# LJ parameters
eps_spce = 0.650
sigma_spce = 0.3166

# PPPM parameters
grid_spacing = 0.08

def create_molecule():
    theta_spce = 109.47*math.pi/180
    roh = 0.1
    pos_spce = [(roh*math.sin(theta_spce/2), roh*math.cos(theta_spce/2),0),
        (roh*math.sin(-theta_spce/2), roh*math.cos(theta_spce/2), 0),
        (0,0,0)]
    mass_spce = np.array([1,1,16])
    rcm = np.sum(mass_spce*pos_spce,axis=0)/np.sum(mass_spce)
    pos_spce -= rcm
    types_spce = ['H','H','OW']
    m_spce = np.sum(mass_spce)
    I_spce = np.zeros((3,3),dtype=np.float64)
    for i in range(3):
        for j in range(3):
            for k in range(3):
                if i == j:
                    I_spce[i,j] += mass_spce[k]*np.linalg.norm(pos_spce[k])**2.0
                I_spce[i,j] -= mass_spce[k]*pos_spce[k,i]*pos_spce[k,j]

    q = 0.8476
    charges_spce = [q/2,q/2,-q]

    return pos_spce, types_spce, charges_spce, m_spce, I_spce

def power_log(x):
    return 2**(math.ceil(math.log(x, 2)))

class Project(FlowProject):
    pass

@FlowProject.label
def equilibrated(job):
    return job.isfile('init.gsd')

@FlowProject.label
def pertains(job):
    global benchmark_name
    return job.statepoint()['benchmark'] == benchmark_name

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

            c = hoomd.context.initialize()
            a = (18.0/(6.022*10**23)*(10**24)/density)**(1./3.)

            system = hoomd.init.create_lattice(n=sp['n'], unitcell=hoomd.lattice.sc(a=a,type_name='H2O'))

            system.particles.types.add('OW')
            system.particles.types.add('H')

            pos_spce, types_spce, charges_spce, m_spce, I_spce = create_molecule()

            for p in system.particles:
                p.mass = m_spce
                p.moment_inertia = (I_spce[0,0],I_spce[1,1],I_spce[2,2])

            reduced_P_unit = 0.0602214
            reduced_T_unit = 0.008314510
            T = T_kelvin*reduced_T_unit
            f = 138.935458
            rigid = md.constrain.rigid()
            rigid.set_param('H2O',positions=pos_spce, types=types_spce, charges=math.sqrt(f)*np.array(charges_spce))
            rigid.create_bodies()

            my_nlist = md.nlist.cell()

            # long cut off so that no long-range correction is needed
            lj = md.pair.lj(r_cut=1.5, nlist=my_nlist)
            lj.pair_coeff.set(['H2O','H'],system.particles.types,epsilon=0,sigma=0,r_cut=False)
            lj.pair_coeff.set('OW','OW',epsilon=eps_spce,sigma=sigma_spce)

            if c.device.comm.num_ranks > 1:
                nx,ny,nz = [power_log(l/grid_spacing) for l in (system.box.Lx, system.box.Ly, system.box.Lz)]
            else:
                nx,ny,nz = [int(l/grid_spacing) for l in (system.box.Lx, system.box.Ly, system.box.Lz)]

            print(system.box.Lx)
            if c.device.comm.rank == 0:
                print('PPPM grid dimensions [{},{},{}]'.format(nx,ny,nz))
                print('Max RMS for 1e-4 rel err (reference RMS) {}'.format(1e-4*f/0.1))

            pppm = md.charge.pppm(nlist=my_nlist,group=hoomd.group.all())
            pppm.set_params(Nx=nx,Ny=ny,Nz=ny, order=5,rcut=0.7)

            integrator = md.integrate.mode_standard(dt=0.002)

            center = hoomd.group.rigid_center()

            nvt = md.integrate.nvt(kT=T,group=center,tau=1.0)
            nvt.randomize_velocities(seed=123)

            hoomd.run(2e3,profile=True)
            hoomd.run(5e4)
            hoomd.dump.gsd('init.gsd', period=None, overwrite=True,group=center)

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
    @project.pre(pertains)
    @project.pre(equilibrated)
    @flow.directives(nranks=nranks)
    @flow.directives(np=nranks)
    @flow.directives(ngpu=ngpu)
    def benchmark(job):
        sp = job.statepoint()

        with job:
            import hoomd
            from hoomd import md

            c = hoomd.context.initialize()
            system = hoomd.init.read_gsd('init.gsd')

            system.particles.types.add('OW')
            system.particles.types.add('H')

            pos_spce, types_spce, charges_spce, _, _ = create_molecule()

            reduced_P_unit = 0.0602214
            reduced_T_unit = 0.008314510
            T = T_kelvin*reduced_T_unit
            f = 138.935458
            rigid = md.constrain.rigid()
            rigid.set_param('H2O',positions=pos_spce, types=types_spce, charges=math.sqrt(f)*np.array(charges_spce))
            rigid.create_bodies()

            my_nlist = md.nlist.cell()

            # long cut off so that no long-range correction is needed
            lj = md.pair.lj(r_cut=1.5, nlist=my_nlist)
            lj.pair_coeff.set(['H2O','H'],system.particles.types,epsilon=0,sigma=0,r_cut=False)
            lj.pair_coeff.set('OW','OW',epsilon=eps_spce,sigma=sigma_spce)

            if c.device.comm.num_ranks > 1:
                nx,ny,nz = [power_log(l/grid_spacing) for l in (system.box.Lx, system.box.Ly, system.box.Lz)]
            else:
                nx,ny,nz = [int(l/grid_spacing) for l in (system.box.Lx, system.box.Ly, system.box.Lz)]

            if c.device.comm.rank == 0:
                print('PPPM grid dimensions [{},{},{}]'.format(nx,ny,nz))
                print('Max RMS for 1e-4 rel err (reference RMS) {}'.format(1e-4*f/0.1))

            pppm = md.charge.pppm(nlist=my_nlist,group=hoomd.group.all())
            pppm.set_params(Nx=nx,Ny=ny,Nz=ny, order=5,rcut=0.7)

            integrator = md.integrate.mode_standard(dt=0.002)

            center = hoomd.group.rigid_center()
            log = hoomd.analyze.log(filename='out.log', quantities=['N','volume','density_kgm3','P_bar', 'potential_energy','temperature','pair_lj_energy','pppm_energy','pair_ewald_energy','pressure'],period=100,overwrite=True)

            def density(timestep):
                return len(center)*18.0/(6.022*10**23)*(10**24)/system.box.get_volume()
            def P_bar(timestep):
                return log.query('pressure')/reduced_P_unit
            log.register_callback('density_kgm3', density)
            log.register_callback('P_bar', P_bar)

            nvt = md.integrate.nvt(kT=T,group=center,tau=1.0)
            #nl.set_params(r_buff=0.6, check_period=7)

            # warm up and autotune
            if c.device.mode == 'gpu':
                hoomd.run(10000)
            else:
                hoomd.run(10000, limit_hours=20.0/3600.0)

            # full benchmark
            tps = hoomd.benchmark.series(warmup=0, repeat=4, steps=50000, limit_hours=20.0/3600.0)
            ptps = np.average(tps) * len(center);

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

