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
* Log file period: 10000 time steps
* SDF analysis
    * $x_\mathrm{max} = =0.02$
    * $\delta x = 10^{-4}$
    * period: 50 time steps
    * $n_\mathrm{avg} = 2000$
* DCD dump period: 100000
