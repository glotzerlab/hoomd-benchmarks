from __future__ import print_function, division
from hoomd import *
from hoomd import md
import numpy
c = context.initialize()

# Get the workspace output dir for storing benchmark metadata
if len(option.get_user()) == 0:
    workspace = '.';
else:
    workspace = option.get_user()[0]

system = init.read_gsd(filename='init.gsd')

harmonic = md.bond.harmonic(name="tether")
harmonic.bond_coeff.set('tether', k=4., r0=0.)

nl = md.nlist.cell()
dpd = md.pair.dpd(nlist = nl, r_cut=1.0, kT=1., seed=1)
A = 40.0
dpd.pair_coeff.set(system.particles.types, system.particles.types, A=A, gamma= 1.0)
dpd.pair_coeff.set('glycerol', 'polymer', A=2*A, gamma= 1.0)
dpd.pair_coeff.set('hydroxyl', 'polymer', A=2*A, gamma= 1.0)
dpd.pair_coeff.set('hydroxyl', 'core', A=2*A, gamma= 1.0)
dpd.pair_coeff.set('hydroxyl', 'glycerol', A=A/2., gamma= 1.0)
dpd.pair_coeff.set('hydroxyl', 'hydroxyl', A=A/2., gamma= 1.0)
md.integrate.mode_standard(dt=0.01)
md.integrate.nve(group=group.all())

nl.reset_exclusions(exclusions = ['bond', 'body'])
nl.set_params(r_buff=0.35, check_period=2)

# warm up and autotune
if c.on_gpu():
    run(10000)
else:
    run(10000, limit_hours=20.0/3600.0)

# full benchmark
tps = benchmark.series(warmup=0, repeat=4, steps=50000, limit_hours=20.0/3600.0)
ptps = numpy.average(tps) * len(system.particles);

# print out millions of particle time steps per second
if comm.get_rank() == 0:
    print("Hours to complete 10e6 steps: {0}".format(10e6/(ptps/len(system.particles))/3600));
    meta.dump_metadata(filename = workspace+"/metadata.json", user = {'mps': ptps, 'tps': tps});
