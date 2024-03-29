# Copyright (c) 2021-2024 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Lennard-Jones pair potential benchmark."""

import hoomd

from . import md_pair


class MDPairLJ(md_pair.MDPair):
    """Molecular dynamics Lennard-Jones pair potential benchmark.

    See Also:
        `md_pair.MDPair`
    """

    pair_class = hoomd.md.pair.LJ
    pair_params = dict(epsilon=1, sigma=1)
    r_cut = 2.5


if __name__ == '__main__':
    MDPairLJ.main()
