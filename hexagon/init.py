import signac
import sys

project = signac.get_project()

sp = {'phi': .7, 'N': 1048576}
job = project.open_job(sp).init()

print(job)
