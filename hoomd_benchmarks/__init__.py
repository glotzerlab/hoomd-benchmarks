"""HOOMD benchmarks main package."""

from .hpmc_sphere import HPMCSphere
from .md_pair_lj import MDPairLJ
from .md_pair_wca import MDPairWCA

benchmark_classes = [
    HPMCSphere,
    MDPairLJ,
    MDPairWCA,
]
