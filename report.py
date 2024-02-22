# Copyright (c) 2021-2024 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Generate a benchmark report from a run on Great Lakes.

Use to report CPU and GPU benchmark performance in the issue for each
HOOMD-blue release.
"""

import subprocess

import pandas

git_sha = subprocess.run(
    ['git', 'show', '-s', '--format=%H'], capture_output=True, check=True
).stdout
git_sha = git_sha.decode('UTF-8').strip()

print(f'hoomd-benchmarks results using hoomd-benchmarks@{git_sha}')
print()

df_gpu = pandas.read_csv('gpu.csv', index_col=0)

print('A100 GPU:')
print('```')
print(df_gpu)
print('```')

df_cpu = pandas.read_csv('cpu.csv', index_col=0)

print('AMD EPYC 7763 (16 cores used)')
print('```')
print(df_cpu)
print('```')
