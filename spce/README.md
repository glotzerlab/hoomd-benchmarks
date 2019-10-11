# SPC/E water benchmark

The SPC/E water tests performance of the extended simple point charge model for liquid water. It uses rigid bodies
and PPPM electrostatics. PPPM is not comparable in performance to more optimized methods not yet implemented
in HOOMD-blue such as PME (used by GROMACS), therefore absolute performance of this benchmark could be improved.

The SPC/e model has been defined in [H. J. C. Berendsen, J. R. Grigera, T. P. Straatsma, J. Phys. Chem. 1987](https://doi.org/10.1021/j100308a038)

<img src="spce_4096.png" style="width: 280px;"/>

Parameters:

* $N = $ *variable*
* $\rho = 994$ kg m^-3
* $\delta t = 0.002$ fs
* PPPM fourier spacing $\delta l = 0.08$ nm
* Integration: Nos&eacute;-Hoover NVT
    * $\T = 300$ K
    * $\tau=1$ ps

## How to add a new statepoint to the database:

1. Choose a number of particles along one edge of the simple cubic lattice for initialization, e.g.
$n=32$, which initializes $N=n^3=32768$ particles.

```
python init.py 32
```

2. Equilibrate. Login to the compute node, then

    ```
    python ../project.py run -o spce-equilibrate
    ````
