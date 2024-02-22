# Copyright (c) 2021-2024 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Table pair potential benchmark."""

import hoomd
import numpy

from . import md_pair

EVAL_POINTS = 200
R_MIN = 0.5
DEFAULT_R_CUT = 2.5


def lj_energy(r):
    """Compute LJ energy."""
    return 4 * ((1 / r) ** 12 - (1 / r) ** 6)


def lj_force(r):
    """Compute LJ force."""
    return 24 * (2 - r**6) / r**13


class MDPairTable(md_pair.MDPair):
    """Molecular dynamics Table pair potential benchmark.

    See Also:
        `md_pair.MDPair`
    """

    pair_class = hoomd.md.pair.Table

    r = numpy.linspace(R_MIN, DEFAULT_R_CUT, EVAL_POINTS, endpoint=False)

    pair_params = dict(r_min=R_MIN, U=lj_energy(r), F=lj_force(r))
    r_cut = DEFAULT_R_CUT


if __name__ == '__main__':
    MDPairTable.main()
