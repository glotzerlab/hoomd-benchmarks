from hoomd_script import *
import math
import numpy
context.initialize()

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

system = init.read_xml(filename = 'init.xml')

# generate the pair interaction table
cutoff = determineCutoff(potential_k, potential_phi)
table = pair.table(width = 1000)
table.pair_coeff.set('A', 'A', func = EOPP, rmin = 0.5, rmax = cutoff,
                     coeff = dict(k = potential_k, phi = potential_phi))

# Integrate at constant temperature
update.zero_momentum(period = 1000)
integrate.nvt(group = group.all(), tau = 1.0, T = temperature)
integrate.mode_standard(dt = 0.01)

nlist.set_params(r_buff=0.35, check_period=4)

# warm up and autotune
if globals.exec_conf.isCUDAEnabled():
    run(30000)
else:
    run(30000, limit_hours=20.0/3600.0)

# tune.r_buff(warmup=50000, steps=5000)

# full benchmark
tps = benchmark.series(warmup=0, repeat=4, steps=50000, limit_hours=20.0/3600.0)
ptps = numpy.average(tps) * len(system.particles);

# print out millions of particle time steps per second
if comm.get_rank() == 0:
    print("Average particle timesteps per second: {0:.2f} million".format(ptps/1e6));
    meta.dump_metadata(filename = workspace+"/metadata.json", overwrite = True, user = {'mps': ptps, 'tps': tps});
