#! /usr/bin/env python

import sys
import signac

if len(sys.argv) != 6:
    print("Usage: create_workspace benchmark cpu system date name")
    sys.exit(1)

project = signac.contrib.get_project()
statepoint = dict(benchmark=sys.argv[1], cpu=sys.argv[2], system=sys.argv[3], date=sys.argv[4], name=sys.argv[5])
job = project.open_job(statepoint)
d = job.document
print(job.workspace())
