import gsd.hoomd

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    'file',
    type=str,
    help='GSD file.',
)

args = parser.parse_args()

frame = gsd.hoomd.open(args.file, 'r')[0]

print(f"gsd_to_lammps.py {args.file}")
print(f" {frame.particles.N} atoms")
print(" 1 atom types")
print(f" {-frame.configuration.box[0]/2} {frame.configuration.box[0]/2} xlo xhi")
print(f" {-frame.configuration.box[1]/2} {frame.configuration.box[1]/2} ylo yhi")
print(f" {-frame.configuration.box[2]/2} {frame.configuration.box[2]/2} zlo zhi")

print()
print(" Masses")
print()
print(" 1 1.0")

print()
print("Atoms # atomic")
print()
for i,p in enumerate(frame.particles.position):
    print(f" {i+1} 1 {p[0]} {p[1]} {p[2]}")
