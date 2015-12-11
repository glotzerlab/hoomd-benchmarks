# lj-liquid benchmark

The Lennard-Jones liquid benchmark is a classic benchmark for general-purpose
MD simulations. It is representative of the performance HOOMD-blue achieves
with straight pair potential simulations.

<img src="lj-liquid/lj-liquid.png" style="width: 280px;"/>

Parameters:

* $N = 64000$
* $\rho = 0.382$
* $r_\mathrm{cut} = 3.0$
* $\epsilon = 1.0$
* $\sigma = 1.0$
* $\delta t = 0.005$
* Integration: Nose-hoover NVT $T=1.2$, $\tau=0.5$
