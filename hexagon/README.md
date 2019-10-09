# hexagon benchmark

The hexagon benchmark runs a system of $1024^2$ hexagons using hard particle Monte Carlo.
At this density, the system is in the middle of the hexatic phase. This model is used in the research article:
[J. A. Anderson, J. Antonaglia, J. A. Millan, M. Engel, and S. C. Glotzer, Phys. Rev. X, vol. 7, no. 2, p. 21001, Apr. 2017.](http://dx.doi.org/10.1103/PhysRevX.7.021001)

<img src="hexagon/hexagon.png" style="width: 280px;"/>

Parameters:

* $N = 1,048,576$
* Hard particle Monte Carlo
    * Vertices: [[0.5,0],[0.25,0.433012701892219],[-0.25,0.433012701892219],[-0.5,0],[-0.25,-0.433012701892219],[0.25,-0.433012701892219]]
    * $d = 0.17010672166874857$
    * $a = 1.0471975511965976$
    * $n_\mathrm{select} = 4$

How to run:

1. Add your execution configuration to the list in `init_exec_confs.py`:
    **mode** (str): either **gpu** or **cpu**
    **gpu_ids** (list): list of GPUs per MPI rank to execute on, e.g. `0` or `0,1,2`
    **nranks** (int): Number of MPI ranks for domain decomposition

    Then, execute

    ```
    python init_exec_confs.py
    ```

2. Equilibrate, if necessary, and execute benchmark on a workstation or compute node, or submit cluster job

    ```
    mpirun -np <number of ranks> python project.py run # executes all pending operations
    ```

    or

    ```
    python project.py submit # submit pending operations to cluster
    ```

    The output is stored in the [signac job document](https://docs.signac.io/en/latest/projects.html), in a `dict` entry with
    the name of the execution configuration as key (e.g., `gpu_nranks1`). Inspect with

    ```
    signac document
    ```

