# Copyright (c) 2021-2023 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Benchmark GSD writes."""

import hoomd
from . import writer


class GSDLog(writer.Writer):
    """Log-only GSD benchmark.

    Args:
        kwargs: Keyword arguments accepted by ``GSD.__init__``

    See Also:
        `write_gsd.GSD`
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # 8 bytes of data. Unknown amount of overhead.
        self.bytes_per_step = 28 / 1024**2

    def make_writer(self):
        """Make the GSD writer object for benchmarking."""
        logger = hoomd.logging.Logger(categories=['scalar'])
        logger[('value')] = (lambda: 42, 'scalar')

        return hoomd.write.HDF5Log(trigger=hoomd.trigger.Periodic(1),
                                   filename='write_hdf5_log.h5',
                                   mode='w',
                                   logger=logger)


if __name__ == '__main__':
    GSDLog.main()
