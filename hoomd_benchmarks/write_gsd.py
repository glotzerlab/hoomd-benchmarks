# Copyright (c) 2021-2023 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Benchmark GSD writes."""

import hoomd

from . import writer

DEFAULT_MAXIMUM_WRITE_BUFFER_SIZE = 64 * 1024 * 1024


class GSD(writer.Writer):
    """GSD benchmark.

    Args:
        kwargs: Keyword arguments accepted by ``Benchmark.__init__``

    See Also:
        `common.Benchmark`
    """

    def __init__(self,
                 maximum_write_buffer_size=DEFAULT_MAXIMUM_WRITE_BUFFER_SIZE,
                 **kwargs):
        self.maximum_write_buffer_size = maximum_write_buffer_size

        super().__init__(**kwargs)

        self.bytes_per_step = self.N * 4 * 3 / 1024**2

    @staticmethod
    def make_argument_parser():
        """Make an ArgumentParser instance for benchmark options."""
        parser = writer.Writer.make_argument_parser()
        parser.add_argument('--maximum_write_buffer_size',
                            type=int,
                            default=DEFAULT_MAXIMUM_WRITE_BUFFER_SIZE,
                            help='Maximum size of the write buffer (in bytes).')
        return parser

    def make_writer(self):
        """Make the GSD writer object for benchmarking."""
        writer = hoomd.write.GSD(trigger=hoomd.trigger.Periodic(1),
                                 filename='write_gsd.gsd',
                                 mode='wb')

        try:
            writer.dynamic = ['particles/position']
        except hoomd.error.TypeConversionError:
            pass

        writer.maximum_write_buffer_size = self.maximum_write_buffer_size

        return writer


if __name__ == '__main__':
    GSD.main()
