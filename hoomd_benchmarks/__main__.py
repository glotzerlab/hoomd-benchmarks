from . import hard_sphere_mc, lj_pair_md, wca_pair_md, common
import numpy

parser = common.make_common_argument_parser()
args = parser.parse_args()
args.device = common.make_hoomd_device(args)

modules = [hard_sphere_mc, lj_pair_md, wca_pair_md]
for module in modules:
    performance = module.benchmark(**vars(args))
    name = module.__name__.split('.')[-1]

    if args.device.communicator.rank == 0:
        print(f'{name}: {numpy.mean(performance)}')
