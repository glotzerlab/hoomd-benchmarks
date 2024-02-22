# Copyright (c) 2021-2024 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""OPP pair potential benchmark."""

import hoomd

from . import md_pair


class MDPairOPP(md_pair.MDPair):
    """Molecular dynamics OPP pair potential benchmark.

    See Also:
        `md_pair.MDPair`
    """

    pair_class = hoomd.md.pair.OPP
    pair_params = dict(
        {
            'C1': 1.7925807855607998,
            'C2': 1.7925807855607998,
            'eta1': 15,
            'eta2': 3,
            'k': 7.0,
            'phi': 5.5,
        }
    )
    r_cut = 2.557


if __name__ == '__main__':
    MDPairOPP.main()
