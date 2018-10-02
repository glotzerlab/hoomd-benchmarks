from hoomd import *
from hoomd import md
import math
import numpy
import os
import sys
c = context.initialize()

# Get the workspace output dir for storing benchmark metadata
if len(option.get_user()) == 0:
    workspace = '.';
else:
    workspace = option.get_user()[0]

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

d = os.path.dirname(sys.argv[0])
system = init.read_gsd(filename=os.path.join(d,'init.gsd'))

# generate the pair interaction table
cutoff = determineCutoff(potential_k, potential_phi)
nl = md.nlist.cell()
table = md.pair.table(nlist = nl, width = 1000)
table.pair_coeff.set('A', 'A', func = EOPP, rmin = 0.5, rmax = cutoff,
                     coeff = dict(k = potential_k, phi = potential_phi))

# Integrate at constant temperature
md.update.zero_momentum(period = 1000)
md.integrate.nvt(group = group.all(), tau = 1.0, kT = temperature)
md.integrate.mode_standard(dt = 0.01)

nl.set_params(r_buff=0.35, check_period=4)

# warm up and autotune
if c.on_gpu():
    run(30000)
else:
    run(30000, limit_hours=20.0/3600.0)

# tune.r_buff(warmup=50000, steps=5000)

# full benchmark
tps = benchmark.series(warmup=0, repeat=4, steps=50000, limit_hours=20.0/3600.0)
ptps = numpy.average(tps) * len(system.particles);

# print out millions of particle time steps per second
if comm.get_rank() == 0:
    print("Hours to complete 10e6 steps: {0}".format(10e6/(ptps/len(system.particles))/3600));
    meta.dump_metadata(filename = workspace+"/metadata.json", user = {'mps': ptps, 'tps': tps});
