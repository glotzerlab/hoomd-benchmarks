#! /usr/bin/env hoomd
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

system = init.read_gsd('init.gsd')

# force field setup
harmonic = md.bond.harmonic()
harmonic.bond_coeff.set('polymer', k=330.0, r0=0.84)
nl = md.nlist.cell()
lj = md.pair.lj(nlist = nl, r_cut=3.0)
lj.pair_coeff.set('A', 'A', epsilon=1.0, sigma=1.0, alpha=0.0)
lj.pair_coeff.set('A', 'B', epsilon=1.0, sigma=1.0, alpha=0.0)
lj.pair_coeff.set('B', 'B', epsilon=1.0, sigma=1.0, alpha=1.0)

# NVT integration
all = group.all()
md.integrate.mode_standard(dt=0.005)
md.integrate.nvt(group=all, kT=1.2, tau=0.5)

nl.set_params(r_buff=0.4, check_period=5)

# warm up and autotune
if c.on_gpu():
    run(30000)
else:
    run(30000, limit_hours=20.0/3600.0)

# tune.r_buff(warmup=5000, steps=500)

# full benchmark
tps = benchmark.series(warmup=0, repeat=4, steps=50000, limit_hours=20.0/3600.0)
ptps = numpy.average(tps) * len(system.particles);

# print out millions of particle time steps per second
if comm.get_rank() == 0:
    print("Hours to complete 10e6 steps: {0}".format(10e6/(ptps/len(system.particles))/3600));
    meta.dump_metadata(filename = workspace+"/metadata.json", user = {'mps': ptps, 'tps': tps});
