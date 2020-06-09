from . import operations

# add benchmark configurations
def init(project, configs):
    for conf in configs:
        operations.add_benchmark(project, mode=conf['mode'], gpu_ids=conf['gpu_ids'], nranks=conf['nranks'])
        operations.add_profile(project, mode=conf['mode'], gpu_ids=conf['gpu_ids'], nranks=conf['nranks'])
