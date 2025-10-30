# Copyright (c) 2021-2025 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

import re
from subprocess import Popen, PIPE, STDOUT

import argparse
import json

PARTICLE_STEPS = 2**24

parser = argparse.ArgumentParser()

parser.add_argument(
    '--suffix',
    type=str,
    help='JSON filename suffix.',
    required=True
)
args = parser.parse_args()

n = 256

n_list = []
lj_performance_list = []

tps_matcher = re.compile(r"(\d+.\d+) timesteps/s")

while n <= 2**20:
    n_list.append(n)
    
    steps = max(PARTICLE_STEPS // n, 32)
    input_file = f"hard_sphere_{n}_0.8442_3.data"

    script = f"""units lj
    dimension 3
    atom_style atomic
    boundary p p p

    read_data {input_file}

    velocity	all create 1.2 1 loop geom

    pair_style	lj/cut 2.5
    pair_coeff	1 1 1.0 1.0 2.5

    neighbor	0.3 bin
    neigh_modify	delay 0 every 1 check yes

    fix	1 all langevin 1.0 1.0 0.1 1530917
    fix 2 all nve

    run		{steps}
    """

    print(f"Executing LAMMPS: n={n}")
    lmp = Popen(['lmp'], stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True)
    stdout_data = lmp.communicate(input=script)[0]
    match = tps_matcher.search(stdout_data)
    tps = float(match.group(1))
    
    lj_performance = (1 / tps) * 1e9 / 3600
    lj_performance_list.append(lj_performance)
    
    n *= 2

with open(f"lj-{args.suffix}.json", "w") as f:
    json.dump({"n": n_list, "performance": lj_performance_list}, f)
