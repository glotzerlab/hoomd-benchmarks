# quasicrystal benchmark

The quasicrystal benchmark runs a system of particles with an oscillatory pair potential that forms an icosahedral
quasicrystal. This model is used in the research article:
[Engel M, et. al. (2015) Computational self-assembly of a one-component icosahedral quasicrystal, Nature materials 14(January), p. 109-116,](http://dx.doi.org/10.1038/NMAT4152)

<img src="quasicrystal.jpeg" style="width: 280px;"/>

Parameters:

* $N = $ *variable*
* $\rho = 0.03$
* Tabulated pair force
    * $$V = \frac{1}{r^{15}} + \frac{\cos(k (r - 1.25) - \phi)}{r^3}$$
    * $k = 6.25$
    * $\phi = 0.62$
* Integration: Nos&eacute;-Hoover NVT
    * $T=0.18$
    * $\tau=1.0$
    * $\delta t = 0.01$

How to run:

1. Choose a number of particles along one edge of the simple cubic lattice for initialization, e.g.
$n=50$, which initializes $N=n^3=125000$ particles.

```
python init.py 50
```

2. Add your execution configuration to the list in `init_exec_confs.py`:

    **mode** (str): either **gpu** or **cpu**

    **gpu_ids** (list): list of GPUs per MPI rank to execute on, e.g. `0` or `0,1,2`

    **nranks** (int): Number of MPI ranks for domain decomposition

    Then, execute

    ```
    python init_exec_confs.py
    ```

3. Equilibrate, if necessary, and execute benchmark on a workstation or compute node, or submit cluster job

    ```
    mpirun -np <number of ranks> python project.py run # executes all pending operations
    ```

    or

    ```
    python project.py submit # submit pending operations to cluster
    ```

    The output is stored in the [signac job document](https://docs.signac.io/en/latest/projects.html), in a `dict` entry with
    the name of the execution configuration as key (e.g., `gpu_np1`). Inspect with

    ```
    signac document
    ```
