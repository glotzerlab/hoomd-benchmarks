# Copyright (c) 2021-2025 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

import sys
import json

import hoomd
from hoomd_benchmarks.md_pair_lj import MDPairLJ
from hoomd_benchmarks.hpmc_octahedron import HPMCOctahedron

PARTICLE_STEPS = 2**22

n = 256
if len(sys.argv) > 1 and sys.argv[1] == 'GPU':
    device = hoomd.device.GPU()
    suffix = 'gpu'
else:
    device = hoomd.device.CPU()
    suffix = 'cpu'

n_list = []
lj_performance_list = []
octahedron_performance_list = []

while n <= 2**12:
    n_list.append(n)
    
    steps = max(PARTICLE_STEPS // n, 16)
    lj = MDPairLJ(N = n, rho=0.8442, warmup_steps = steps//4, benchmark_steps=steps,
        verbose=True, device=device)
    lj_performance = (1 / lj.execute()[0]) * 1e9 / 3600
    lj_performance_list.append(lj_performance)
    

    octahedron = HPMCOctahedron(N = n, rho=0.8442, warmup_steps = steps//4, benchmark_steps=steps,
        verbose=True, device=device)
    octahedron_performance = (1 / octahedron.execute()[0]) * 1e9 / 3600
    octahedron_performance_list.append(octahedron_performance)

    n *= 2

with open(f"lj-{suffix}.json", "w") as f:
    json.dump({"n": n_list, "performance": lj_performance_list}, f)

with open(f"octahedron-{suffix}.json", "w") as f:
    json.dump({"n": n_list, "performance": octahedron_performance_list}, f)
