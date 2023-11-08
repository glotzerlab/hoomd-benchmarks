# Copyright (c) 2021-2023 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Benchmark GSD writes."""

import hoomd

from . import write_gsd


class GSDLog(write_gsd.GSD):
    """Log-only GSD benchmark.

    Args:
        kwargs: Keyword arguments accepted by ``GSD.__init__``

    See Also:
        `write_gsd.GSD`
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # 24 bytes of index + 4 bytes of logged data
        self.bytes_per_step = 28 / 1024**2

    def make_writer(self):
        """Make the GSD writer object for benchmarking."""
        logger = hoomd.logging.Logger(categories=['scalar', 'string'])
        logger[('value')] = (lambda: 42, 'scalar')

        return hoomd.write.GSD(trigger=hoomd.trigger.Periodic(1),
                               filename='write_gsd_log.gsd',
                               mode='wb',
                               filter=hoomd.filter.Null(),
                               logger=logger)


if __name__ == '__main__':
    GSDLog.main()
