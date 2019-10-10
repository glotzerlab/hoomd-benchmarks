import signac
import sys

project = signac.get_project()

sp = {'benchmark': 'microsphere', 'N': 1428364}
job = project.open_job(sp).init()

print(job)
