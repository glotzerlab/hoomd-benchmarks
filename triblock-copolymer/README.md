# triblock-copolymer benchmark

The triblock copolymer benchmark runs a system of A10-B7-A10 triblock copolymers that form
spherical micelles which organize into a bcc phase. This model is used in the research article:
[Anderson et. al. - Coarse-Grained Simulations of Gels of Nonionic Multiblock Copolymers with Hydrophobic Groups](http://dx.doi.org/10.1021/ma061120f)

It is representative of the performance HOOMD-blue achieves linearly bonded bead spring polymers.

<img src="triblock-copolymer/triblock-copolymer.png" style="width: 280px;"/>

Parameters:

* $N = 64017$
* $\rho = 0.382$
* $r_\mathrm{cut} = 3.0$
* Lennard-Jones pair force
* $\epsilon = 1.0$
* $\sigma = 1.0$
* $\alpha_\mathrm{AA}=0$, $\alpha_\mathrm{AB}=0$, $\alpha_\mathrm{BB}=1$
* $\delta t = 0.005$
* Integration: Nose-hoover NVT $T=1.2$, $\tau=0.5$
