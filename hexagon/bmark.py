from __future__ import print_function
from __future__ import division
from hoomd import *
from hoomd import hpmc
import numpy
c = context.initialize();

# Get the workspace output dir for storing benchmark metadata
if len(option.get_user()) == 0:
    workspace = '.';
else:
    workspace = option.get_user()[0]

# read parameters
phi = 0.7000;
fname_base = 'phi-{0:5.4f}'.format(phi);

# read the initial config or restart file
system = init.read_gsd(filename='init.gsd')

# setup the MC integration
mc = hpmc.integrate.convex_polygon(seed=20, d=0.17010672166874857, a=1.0471975511965976, nselect=4);
mc.shape_param.set('A', vertices=[[0.5,0],[0.25,0.433012701892219],[-0.25,0.433012701892219],[-0.5,0],[-0.25,-0.433012701892219],[0.25,-0.433012701892219]]);

# setup the logging
analyze.log(filename=fname_base+".log", period=10000, quantities=['hpmc_sweep', 'hpmc_translate_acceptance', 'hpmc_rotate_acceptance', 'hpmc_d', 'hpmc_a', 'hpmc_move_ratio', 'hpmc_overlap_count'], phase=0)
hpmc.analyze.sdf(mc=mc, filename=fname_base+'-sdf.dat', xmax=0.02, dx=1e-4, navg=2000, period=50)

# dump configurations to dcd
dump.dcd(filename=fname_base+".dcd", period=500000, angle_z=True, phase=0)

# dump restart files
gsd_restart = dump.gsd(filename=fname_base+"-restart.gsd", period=100000, group=group.all(), truncate=True);

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

