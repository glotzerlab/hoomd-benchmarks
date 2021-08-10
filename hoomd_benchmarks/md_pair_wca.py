"""WCA pair potential benchmark."""

import hoomd
from . import md_pair


class MDPairWCA(md_pair.MDPair):
    """Molecular dynamics WCA pair potential benchmark.

    See Also:
        `md_pair.MDPair`
    """
    pair_class = hoomd.md.pair.LJ
    pair_params = dict(epsilon=1, sigma=1)
    r_cut = 2**(1 / 6)


if __name__ == '__main__':
    MDPairWCA.main()
