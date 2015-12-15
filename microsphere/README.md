# microsphere benchmark

The microrsphere benchmark runs a system of star polymers in an explicit solvent using DPD.
These organize into a microspherical droplet. This model is used in the research article:
[Zhang et. al. Simultaneous Nano- and Microscale Control of Nanofibrous Microspheres Self-Assembled from Star-Shaped Polymers. Advanced Materials, pages 3947–3952 , 2015.](http://dx.doi.org/10.1002/adma.201501329)

<img src="microsphere/microsphere.png" style="width: 280px;"/>

Parameters:

* $N = 1,428,364$
* $r_\mathrm{cut} = 1.0$
* DPD pair force
    * See `bmark.py` for full force field specification.
* Harmonic bond force
* Integration: DPD thermostat
    * $T=1.0$
    * $\delta t = 0.01$
