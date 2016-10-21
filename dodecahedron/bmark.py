from __future__ import print_function
from __future__ import division
from hoomd import *
from hoomd import hpmc
import math
import numpy
c = context.initialize();

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

# Get the workspace output dir for storing benchmark metadata
if len(option.get_user()) == 0:
    workspace = '.';
else:
    workspace = option.get_user()[0]

# read the initial config or restart file
system = init.read_gsd(filename='init.gsd')

# setup the MC integration
mc = hpmc.integrate.convex_polyhedron(seed=10, d=0.3, a=0.26, max_verts=20);
mc.shape_param.set("A", vertices=points);

# warm up and autotune
if c.on_gpu():
    run(1000)
else:
    run(1000, limit_hours=20.0/3600.0)

# full benchmark
tps = benchmark.series(warmup=0, repeat=4, steps=50000, limit_hours=20.0/3600.0)

# correct get_mps based on average of TPS values (get_mps is only for the last run())
mps = mc.get_mps() / tps[-1] * numpy.mean(tps);

# print out millions of particle time steps per second
if comm.get_rank() == 0:
    print("Hours to complete 10e6 steps: {0}".format(10e6/(mps/len(system.particles))/3600));
    meta.dump_metadata(filename = workspace+"/metadata.json", user = {'mps': mps, 'tps': tps});
