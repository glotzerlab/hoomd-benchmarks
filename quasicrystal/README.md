# quasicrystal benchmark

The quasicrystal benchmark runs a system of particles with an oscillatory pair potential that forms an icosahedral
quasicrystal. This model is used in the research article:
[Engel M, et. al. (2015) Computational self-assembly of a one-component icosahedral quasicrystal, Nature materials 14(January), p. 109-116,](http://dx.doi.org/10.1038/NMAT4152)

<img src="quasicrystal/quasicrystal.jpeg" style="width: 280px;"/>

Parameters:

* $N = 100000$
* $\rho = 0.03$
* Tabulated pair force
    * $$V = \frac{1}{r^{15}} + \frac{\cos(k (r - 1.25) - \phi)}{r^3}$$
    * $k = 6.25$
    * $\phi = 0.62$
* Integration: Nos&eacute;-Hoover NVT
    * $T=0.18$
    * $\tau=1.0$
    * $\delta t = 0.01$
