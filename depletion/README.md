# depletion benchmark

The depletion benchmark runs a system of $1000$ cuboctahedra, with depletants at a size ratio $q=0.25$ and a reservoir density of $\phi_{dep}^r=0.80$.

Under these conditions, the cuboctahedra forms a dense sheared BCC crystal. The depletion method was described in:
[Glaser, J et al. A parallel algorithm for implicit depletant simulations. Journal of Chemical Physics, 2015.](http://scitation.aip.org/content/aip/journal/jcp/143/18/10.1063/1.4935175)
The cuboctahedra with depletion system was studied in the research article:
[Karas AS et al. Using depletion to control colloidal crystal assemblies of hard cuboctahedra. Soft Matter, 2015](http://pubs.rsc.org/en/content/articlelanding/2016/sm/c6sm00620e)

<img src="depletion/depletion.png" style="width: 280px;"/>

Parameters:

* $N = $ *variable*
* Hard particle Monte Carlo
    * Polyhedron Vertices: [[-0.53139075, -0.53139075, 0], [-0.53139075, 0.53139075, 0], [0.53139075, -0.53139075, 0], [0.53139075, 0.53139075, 0], [0, -0.53139075, -0.531390750], [0, -0.53139075, 0.53139075], [0, 0.53139075, -0.53139075], [0, 0.53139075, 0.53139075], [-0.53139075, 0, -0.53139075], [-0.53139075, 0, 0.53139075], [0.53139075, 0, -0.53139075], [0.53139075, 0, 0.53139075]]
    * Polyhedron sweep radius: 0
    * Depletant vertices: []
    * Depletant sweep radius: $0.7515*0.25 = 0.1879$
    * $d = 0.0351 $
    * $a = 0.0544 $
    * $nR = 28.8 $
    * ntrial = 0

How to run:

1. Choose a number of particles along one edge of the simple cubic lattice for initialization, e.g.
$n=10$, which initializes $N=n^3=1000$ particles.

```
python init.py 10
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
    the name of the execution configuration as key (e.g., `gpu_nranks1`). Inspect with

    ```
    signac document
    ```
