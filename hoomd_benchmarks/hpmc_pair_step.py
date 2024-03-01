# Copyright (c) 2021-2024 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Step HPMC pair potential benchmark."""

import hoomd

from . import hpmc_pair


class HPMCPairStep(hpmc_pair.HPMCPair):
    """HPMC Step pair potential benchmark.

    See Also:
        `hpmc_pair.HPMCPair`
    """

    pair_class = getattr(hoomd.hpmc.pair, 'Step', None)
    pair_params = dict(epsilon=[-0.2], r=[1.5])

    code = """
            float rsq = dot(r_ij, r_ij);
            float r_cut = 1.5;
            float r_cutsq = r_cut * r_cut;

            if (rsq >= r_cutsq)
                return 0.0f;

            return -0.2;
            """


if __name__ == '__main__':
    HPMCPairStep.main()
