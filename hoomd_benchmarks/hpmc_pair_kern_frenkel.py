# Copyright (c) 2021-2024 The Regents of the University of Michigan
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Kern-Frenkel HPMC pair potential benchmark."""

import hoomd

from . import hpmc_pair
from .configuration.hard_sphere import make_hard_sphere_configuration


class HPMCPairKernFrenkel(hpmc_pair.HPMCPair):
    """HPMC Kern-Frenkel pair potential benchmark.

    See Also:
        `hpmc_pair.HPMCPair`
    """

    r_cut = 1.5
    diameter = 1.0
    pair_class = getattr(hoomd.hpmc.pair, 'AngularStep', None)

    code = f"""
            const vec3<float> director(1, 0, 0);
            vec3<float> director_i = rotate(q_i, director);
            vec3<float> director_j = rotate(q_j, director);

            vec3<float> r_hat_ij = r_ij / sqrtf(dot(r_ij, r_ij));
            bool patch_on_i_is_aligned = dot(director_i, r_hat_ij) >= cos(0.5);
            bool patch_on_j_is_aligned = dot(director_j, -r_hat_ij) >= cos(0.5);

            float rsq = dot(r_ij, r_ij);
            float r_cut = { r_cut };
            float r_cutsq = r_cut * r_cut;

            if (patch_on_i_is_aligned && patch_on_j_is_aligned && rsq < r_cutsq)
                return -0.2f;

            return 0.0f;
            """

    def make_simulation(self):
        """Make the Simulation object."""
        path = make_hard_sphere_configuration(
            N=self.N,
            rho=self.rho,
            dimensions=self.dimensions,
            device=self.device,
            verbose=self.verbose,
        )

        integrator = hoomd.hpmc.integrate.Sphere(default_d=0)
        integrator.shape['A'] = dict(diameter=self.diameter, orientable=True)

        sim = hoomd.Simulation(device=self.device, seed=10)
        sim.create_state_from_gsd(filename=str(path))

        if self.mode == 'compiled':
            square_well = hoomd.hpmc.pair.Step()
            square_well.params[('A', 'A')] = dict(epsilon=[-0.2], r=[self.r_cut])

            pair = self.pair_class(isotropic_potential=square_well)
            pair.mask['A'] = dict(directors=[(0, 0, 1)], deltas=[0.5])
            integrator.pair_potentials = [pair]
        elif self.mode == 'code':
            patch = hoomd.hpmc.pair.user.CPPPotential(
                code=self.code, r_cut=self.r_cut, param_array=[]
            )
            integrator.pair_potential = patch
        else:
            raise ValueError('Invalid mode: ', self.mode)

        sim.operations.integrator = integrator

        return sim


if __name__ == '__main__':
    HPMCPairKernFrenkel.main()
