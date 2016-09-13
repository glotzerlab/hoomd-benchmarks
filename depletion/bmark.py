from __future__ import print_function
from __future__ import division
from hoomd import *
from hoomd import hpmc
import numpy, math

c = context.initialize();

# Get the workspace output dir for storing benchmark metadata
if len(option.get_user()) == 0:
    workspace = '.';
else:
    workspace = option.get_user()[0]

# read parameters
phi = 0.50
pf_R = 0.80 #Volume density of depletants in system free volume
q = 0.25 #Ratio of depletant radius to polyhedra circumsphere radius
fname = 'polyhedra_depletion_test'

#Define the vertices of a cuboctahedra
v_amplitude = 0.53139075
verts = []
for i in [-v_amplitude, v_amplitude]:
    for j in [-v_amplitude, v_amplitude]:
        verts.append([i, j, 0.0])
for j in [-v_amplitude, v_amplitude]:
    for k in [-v_amplitude, v_amplitude]:
        verts.append([0.0, j, k])
for i in [-v_amplitude, v_amplitude]:
    for k in [-v_amplitude, v_amplitude]:
        verts.append([i, 0.0, k])

circumsphere_rad = 0.7515
depletant_rad = circumsphere_rad*q
depletant_V = (4.0/3) * math.pi * math.pow(depletant_rad, 3)
nR = pf_R / depletant_V #Number density of depletants in system free volume

# read the initial config or restart file
system = init.read_gsd(filename='init.gsd')

# setup the MC integration
mc = hpmc.integrate.convex_spheropolyhedron(seed=20, d=0.0351, a=.0544, nselect=4, implicit=True, max_verts = len(verts));
mc.shape_param.set("Poly", vertices=verts, sweep_radius=0)
mc.shape_param.set("Depletant", vertices=[], sweep_radius=depletant_rad)

mc.set_params(ntrial=0)
mc.set_params(nR=nR)
mc.set_params(depletant_type='Depletant')

# setup the logging
free_vol = hpmc.compute.free_volume(mc=mc, seed=123, nsample=50000, test_type='Depletant')
analyze.log(filename=fname+".log", period=1000, quantities=['hpmc_sweep', 'hpmc_translate_acceptance', 'hpmc_rotate_acceptance', 'hpmc_d', 'hpmc_a', 'hpmc_move_ratio', 'hpmc_overlap_count', 'hpmc_free_volume', 'hpmc_fugacity'], phase=0)

# dump restart files
gsd_restart = dump.gsd(filename=fname+"-restart.gsd", period=100000, group=group.all(), truncate=True);

# warm up and autotune
if c.on_gpu():
    run(2000)
else:
    run(2000, limit_hours=20.0/3600.0)

# full benchmark
tps = benchmark.series(warmup=0, repeat=4, steps=10000, limit_hours=20.0/3600.0)

# correct get_mps based on average of TPS values (get_mps is only for the last run())
mps = mc.get_mps() / tps[-1] * numpy.mean(tps);

# print out millions of particle time steps per second
if comm.get_rank() == 0:
    print("Hours to complete 10e6 steps: {0}".format(10e6/(mps/len(system.particles))/3600));
    meta.dump_metadata(filename = workspace+"/metadata.json", user = {'mps': mps, 'tps': tps});

