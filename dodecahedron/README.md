# dodecahedron benchmark

The dodecahedron benchmark runs a fluid of dodecahedra using hard particle Monte Carlo.
This is a synthetic benchmark of 3D convex polyhedra performance.

<img src="dodecahedron.png" style="width: 280px;"/>

Parameters:

* $N = $ *variable*
* Hard particle Monte Carlo
    * Vertices: *see dodecahdron/bmark.py*
    * $d = 0.3$
    * $a = 0.26$
    * density $\phi = 0.5$
    * $n_\mathrm{select} = 4$

## How to add a new statepoint to the database:

1. Choose a number of particles along one edge of the simple cubic lattice for initialization, e.g.
$n=50$, which initializes $N=n^3=125000$ particles.

```
python init.py 50
```

2. Compress to the target density. Login to the compute node, then

    ```
    python ../project.py run -o dodecahedron-compress
    ```
