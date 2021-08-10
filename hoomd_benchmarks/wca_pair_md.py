"""WCA pair potential benchmark."""

import hoomd
from . import common_pair_md

PAIR_CLASS = hoomd.md.pair.LJ
PAIR_PARAMS = dict(epsilon=1, sigma=1)
R_CUT = 2**(1.0 / 6.0)


def benchmark(device,
              N=common_pair_md.DEFAULT_N,
              rho=common_pair_md.DEFAULT_RHO,
              dimensions=common_pair_md.DEFAULT_DIMENSIONS,
              **kwargs):
    """Run the WCA pair potential benchmark.

    Args:
        device (hoomd.device.Device): Device object to execute on.
        N (int): The number of particles.
        rho (float): The number density.
        dimensions (int): The number of dimensions (2 or 3).

        kwargs (dict): Capture other command line arguments in order to pass
          them to `common.run_simulation_benchmark`.

    Returns:
        list[float]: The performance in time steps per second measured at each
            benchmark stage.
    """
    return common_pair_md.benchmark(device=device,
                                    pair_class=PAIR_CLASS,
                                    pair_params=PAIR_PARAMS,
                                    r_cut=R_CUT,
                                    **kwargs)


if __name__ == '__main__':
    common_pair_md.main(pair_class=PAIR_CLASS,
                        pair_params=PAIR_PARAMS,
                        r_cut=R_CUT)
