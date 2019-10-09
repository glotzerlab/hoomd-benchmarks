import signac

# add your own execution configurations as necessary
exec_confs = [
    {'mode': 'cpu', 'gpu_ids': [], 'nranks': 8}, # 8 CPU cores
    {'mode': 'gpu', 'gpu_ids': [], 'nranks': 1}, # 1 GPU
#    {'mode': 'gpu', 'gpu_ids': [0,1], 'nranks': 1}, # two GPUs using NVLINK
    ]

project = signac.get_project()
project.doc['exec_confs'] = exec_confs

