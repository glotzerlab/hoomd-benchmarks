#! /usr/bin/env hoomd
from __future__ import print_function, division
from hoomd_script import *
import numpy

system = init.create_random(N=64000, phi_p=0.2)
lj = pair.lj(r_cut=3.0)
lj.pair_coeff.set('A', 'A', epsilon=1.0, sigma=1.0)

all = group.all()
integrate.mode_standard(dt=0.005)
integrate.nvt(group=all, T=1.2, tau=0.5)

run(200000)

dump.xml('init.xml', vis=True, velocity=True)
