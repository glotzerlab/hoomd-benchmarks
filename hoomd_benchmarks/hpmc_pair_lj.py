# Copyright (c) 2021-2024 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Lennard-Jones HPMC pair potential benchmark."""

import hoomd

from . import hpmc_pair


class HPMCPairLJ(hpmc_pair.HPMCPair):
    """HPMC Lennard-Jones pair potential benchmark.

    See Also:
        `hpmc_pair.HPMCPair`
    """

    r_cut = 2.5
    diameter = 0
    pair_class = getattr(hoomd.hpmc.pair, 'LennardJones', None)
    pair_class_args = {'mode': 'shift'}
    pair_params = dict(epsilon=1, sigma=1, r_cut=r_cut)

    code = f"""
            float rsq = dot(r_ij, r_ij);
            float r_cut = { r_cut };
            float r_cutsq = r_cut * r_cut;

            if (rsq >= r_cutsq)
                return 0.0f;

            float sigma = 1.0;
            float sigsq = sigma * sigma;
            float rsqinv = sigsq / rsq;
            float r6inv = rsqinv * rsqinv * rsqinv;
            float r12inv = r6inv * r6inv;
            return 4 * 1.0 * (r12inv - r6inv);
            """


if __name__ == '__main__':
    HPMCPairLJ.main()
