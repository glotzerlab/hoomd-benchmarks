from . import operations

# add benchmark configurations
def init(project, configs):
    operations.add_equilibration(project)

    for conf in configs:
        operations.add_benchmark(project, mode=conf['mode'], gpu_ids=conf['gpu_ids'], nranks=conf['nranks'])
