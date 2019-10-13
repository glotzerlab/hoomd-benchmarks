import signac
from flow import FlowProject

class Project(FlowProject):
    pass

benchmarks = [
             'lj_liquid',
             'hexagon',
             'microsphere',
             'quasicrystal',
             'depletion',
             'dodecahedron',
             'spce',
             'patchy_protein'
             ]

from exec_confs import exec_confs

if __name__ == '__main__':
    import importlib
    for b in benchmarks:
        importlib.import_module(b).init(Project, exec_confs)

    Project().main()


