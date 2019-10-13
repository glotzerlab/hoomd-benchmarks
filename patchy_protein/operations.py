import flow
from flow import environments
from flow import FlowProject
import signac
import numpy as np
import math

benchmark_name = 'patchy_protein'

# state point parameters
npatch = 3
patch_select = [0,1,2]
eps = 0.33
phi_p = 0.25
sigma = 0.25
V = 6.167 # excluded volume

# helper functions
def quaternion_from_matrix(T):
    # http://www.euclideanspace.com/maths/geometry/rotations/conversions/matrixToQuaternion/
    tr = np.trace(T)
    if (tr > 0):
        S = math.sqrt(tr+1.0) * 2;
        qw = 0.25 * S;
        qx = (T[2,1] - T[1,2])/S;
        qy = (T[0,2] - T[2,0])/S;
        qz = (T[1,0] - T[0,1])/S;
    elif ((T[0,0] > T[1,1]) and (T[0,0] > T[2,2])):
        S = math.sqrt(1.0+T[0,0]-T[1,1]-T[2,2])*2;
        qw = (T[2,1] - T[1,2]) / S;
        qx = 0.25*S;
        qy = (T[0,1] + T[1,0]) / S;
        qz = (T[0,2] + T[2,0]) / S;
    elif (T[1,1] > T[2,2]):
        S = math.sqrt(1.0 + T[1,1] - T[0,0] - T[2,2])*2
        qw = (T[0,2] - T[2,0]) / S;
        qx = (T[0,1] + T[1,0]) / S;
        qy = 0.25*S;
        qz = (T[1,2] + T[2,1]) /S;
    else:
        S = math.sqrt(1.0 + T[2,2] - T[0,0] - T[1,1])*2;
        qw = (T[1,0] - T[0,1]) / S;
        qx = (T[0,2] + T[2,0]) / S;
        qy = (T[1,2] + T[2,1]) / S;
        qz = 0.25 * S;
    return np.array((qw,qx,qy,qz))

def quat_mult(a,b):
    a = np.array(a)
    b = np.array(b)
    s = a[0]*b[0] - np.dot(a[1:],b[1:])
    v = a[0]*b[1:] + b[0]*a[1:] + np.cross(a[1:],b[1:])
    return np.array((s,v[0],v[1],v[2]))

def load_interfaces(filename):
    interfaces = []
    cur_interface = []
    first_line = True
    natoms = 0
    with open(filename,'r') as f:
        for l in f.readlines():
            if first_line:
                natoms = int(l.split()[2])
                first_line = False
            elif natoms > 0:
                cur_interface.append(int(l)-1)
                if natoms == 1:
                    first_line = True
                    interfaces.append(cur_interface)
                    cur_interface = []
                natoms -= 1
    return interfaces

def create_molecule():
    interfaces = load_interfaces('patchy_protein/interface_atoms.txt')

    atoms_r = np.loadtxt('patchy_protein/1brf.xyzb',usecols=(0,1,2,3,4))
    atoms = atoms_r[:,0:3]/10
    diameters = 2*atoms_r[:,3]/10

    # rotate into frame where moment of inertia is diagonal
    I = np.zeros((3,3),dtype=np.float64)
    for (m,p) in zip([1.0]*len(atoms),atoms):
        I[0,0] += m*(np.dot(p,p) - p[0]*p[0])
        I[0,1] += m*(            - p[0]*p[1])
        I[0,2] += m*(            - p[0]*p[2])
        I[1,0] += m*(            - p[1]*p[0])
        I[1,1] += m*(np.dot(p,p) - p[1]*p[1])
        I[1,2] += m*(            - p[1]*p[2])
        I[2,0] += m*(            - p[2]*p[0])
        I[2,1] += m*(            - p[2]*p[1])
        I[2,2] += m*(np.dot(p,p) - p[2]*p[2])

    # diagonalize
    w, v = np.linalg.eig(I)

    if np.linalg.det(v) < 0.0:
        # left handed matrix, swap
        v[:,[2,1]] = v[:,[1,2]]
        w[[2,1]] = w[[1,2]]

    # rotate into body frame
    qI = quaternion_from_matrix(v)

    for i,a in enumerate(atoms):
        atoms[i] = np.dot(np.transpose(v), a)

    circ_r = np.max(np.linalg.norm(atoms,axis=1))+0.5*np.max(diameters)

    my_types =['sphere']*len(atoms)
    patch_types = set()

    for i,interface_no in enumerate(patch_select):
        for j,a in enumerate(interfaces[2*interface_no+0]):
            my_types[a] = 'patch'+str(i)+'a'
            patch_types.add(my_types[a])
        for j,a in enumerate(interfaces[2*interface_no+1]):
            my_types[a] = 'patch'+str(i)+'b'
            patch_types.add(my_types[a])

    mass = 1.0*len(atoms)
    return atoms, diameters, circ_r, mass, w,  my_types, patch_types

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
        atoms, diameters, circ_r, mass, I,  my_types, patch_types = create_molecule()

        with job:
            import hoomd
            from hoomd import md

            c = hoomd.context.initialize()

            system = hoomd.init.create_lattice(n=sp['n'], unitcell=hoomd.lattice.sc(a=2*circ_r))

            for p in system.particles:
                p.mass = mass
                p.moment_inertia = I

            system.particles.types.add('sphere')
            for t in patch_types:
                system.particles.types.add(t)

            rigid = md.constrain.rigid()
            rigid.set_param('A', positions=list(atoms), types = my_types,diameters=[d-sigma+1 for d in diameters])
            rigid.create_bodies()

            my_nlist = md.nlist.cell()
            slj = md.pair.slj(nlist=my_nlist,name='repulsive',r_cut=False)
            slj.pair_coeff.set(system.particles.types, system.particles.types, epsilon=0,sigma=0,r_cut=False)
            slj.pair_coeff.set('sphere','sphere',epsilon=1.0,sigma=sigma,r_cut=sigma*2**(1./6.))
            slj.pair_coeff.set('sphere',patch_types,epsilon=1.0,sigma=sigma,r_cut=sigma*2**(1./6.))
            slj.pair_coeff.set(patch_types,patch_types,epsilon=1.0,sigma=sigma,r_cut=sigma*2**(1./6.))
            slj.set_params(mode="shift")

            slj_attr = md.pair.slj(nlist=my_nlist,name='attractive',r_cut=False)
            slj_attr.pair_coeff.set(system.particles.types, system.particles.types, epsilon=0,sigma=0,r_cut=False)
            # set up specific interactions
            for i in range(npatch):
                slj_attr.pair_coeff.set('patch'+str(i)+'a','patch'+str(i)+'b', epsilon=eps,sigma=sigma,r_cut=2.5*sigma)

            center = hoomd.group.rigid_center()
            integrator = md.integrate.mode_standard(dt=0.005)
            nvt = md.integrate.nvt(kT=1.0, tau=1.0, group=center)
            nvt.randomize_velocities(seed=123)

            hoomd.run(10000)

            # shrink the box to the target
            compress_steps = 5e4
            L = system.box.Lx
            L_target = (len(center)*V/phi_p)**(1./3.)
            resize=hoomd.update.box_resize(L=hoomd.variant.linear_interp([(0,L),(compress_steps,L_target)]),period=1)
            hoomd.run(compress_steps)
            resize.disable()

            hoomd.run(100000)

            # save output
            hoomd.dump.gsd(period=None, filename='init.gsd', group=center)

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
        atoms, diameters, circ_r, mass, I,  my_types, patch_types = create_molecule()

        with job:
            import hoomd
            from hoomd import md

            device = hoomd.device.GPU(gpu_ids=gpu_ids) if mode == 'gpu' else hoomd.device.CPU()
            c = hoomd.context.initialize(device)
            system = hoomd.init.read_gsd('init.gsd')

            rigid = md.constrain.rigid()
            rigid.set_param('A', positions=list(atoms), types = my_types,diameters=[d-sigma+1 for d in diameters])
            rigid.create_bodies()

            my_nlist = md.nlist.cell()
            slj = md.pair.slj(nlist=my_nlist,name='repulsive',r_cut=False)
            slj.pair_coeff.set(system.particles.types, system.particles.types, epsilon=0,sigma=0,r_cut=False)
            slj.pair_coeff.set('sphere','sphere',epsilon=1.0,sigma=sigma,r_cut=sigma*2**(1./6.))
            slj.pair_coeff.set('sphere',patch_types,epsilon=1.0,sigma=sigma,r_cut=sigma*2**(1./6.))
            slj.pair_coeff.set(patch_types,patch_types,epsilon=1.0,sigma=sigma,r_cut=sigma*2**(1./6.))
            slj.set_params(mode="shift")

            slj_attr = md.pair.slj(nlist=my_nlist,name='attractive',r_cut=False)
            slj_attr.pair_coeff.set(system.particles.types, system.particles.types, epsilon=0,sigma=0,r_cut=False)
            # set up specific interactions
            for i in range(npatch):
                slj_attr.pair_coeff.set('patch'+str(i)+'a','patch'+str(i)+'b', epsilon=eps,sigma=sigma,r_cut=2.5*sigma)

            center = hoomd.group.rigid_center()
            integrator = md.integrate.mode_standard(dt=0.005)
            nvt = md.integrate.nvt(kT=1.0, tau=1.0, group=center)

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
                row['N'] = len(center)
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
