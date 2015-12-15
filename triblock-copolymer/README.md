# triblock-copolymer benchmark

The triblock copolymer benchmark runs a system of A10-B7-A10 triblock copolymers that form
spherical micelles which organize into a bcc phase. This model is used in the research article:
[Anderson, JA et. al. - Coarse-Grained Simulations of Gels of Nonionic Multiblock Copolymers with Hydrophobic Groups. Macromolecules, 39(15):5143–5151, July 2006.](http://dx.doi.org/10.1021/ma061120f)

<img src="triblock-copolymer/triblock-copolymer.png" style="width: 280px;"/>

Parameters:

* $N = 64017$
* $\rho = 0.382$
* Lennard-Jones pair force
    * $r_\mathrm{cut} = 3.0$
    * $\epsilon = 1.0$
    * $\sigma = 1.0$
    * $\alpha_\mathrm{AA}=0$, $\alpha_\mathrm{AB}=0$, $\alpha_\mathrm{BB}=1$
* Harmonic bond force
    * $k = 330$
    * $r_0 = 0.84$
* Integration: Nos&eacute;-Hoover NVT
    * $T=1.2$
    * $\tau=0.5$
    * $\delta t = 0.005$
