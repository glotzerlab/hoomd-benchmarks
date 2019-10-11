import signac
import sys

if len(sys.argv) != 2:
    raise RuntimeError('Invoke with: {} <number of particles along one edge>\n'.format(sys.argv[0]))
n = int(sys.argv[1])
project = signac.get_project()

sp = {'benchmark': 'lj_liquid', 'n': n}
job = project.open_job(sp).init()

print(job)
