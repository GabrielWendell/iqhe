"""Run compact Stage-1 Hamiltonian acceptance checks from the repository root."""

from __future__ import annotations

import sys

import numpy as np

from qhe.models import (
    HarperHofstadterParameters,
    bloch_hamiltonian,
    bloch_hamiltonian_derivatives,
    magnetic_brillouin_zone,
    open_hamiltonian,
    ribbon_hamiltonian,
)
from qhe.validation import hermiticity_residual


def main() -> int:
    params = HarperHofstadterParameters(p=1, q=3, tx=1.0, ty=1.0)
    zone = magnetic_brillouin_zone(params)
    matrices = {
        'open (4 x 5)': open_hamiltonian(4, 5, params),
        'ribbon (Lx=9, ky=0.37)': ribbon_hamiltonian(9, 0.37, params),
        'bloch (kx=0.11, ky=-0.42)': bloch_hamiltonian(0.11, -0.42, params),
    }

    print('Stage-1 convention and Hamiltonian checks')
    print(f'  flux: phi = {params.p}/{params.q} = {params.flux:.8f}')
    print(
        '  magnetic Brillouin zone: '
        f'kx in [{zone.kx_min:.6f}, {zone.kx_max:.6f}), '
        f'ky in [{zone.ky_min:.6f}, {zone.ky_max:.6f})'
    )
    for label, matrix in matrices.items():
        print(f'  {label}: Hermiticity residual = {hermiticity_residual(matrix):.3e}')

    step = 1.0e-7
    kx, ky = 0.11, -0.42
    d_kx, d_ky = bloch_hamiltonian_derivatives(kx, ky, params)
    finite_kx = (bloch_hamiltonian(kx + step, ky, params) - bloch_hamiltonian(kx - step, ky, params)) / (2.0 * step)
    finite_ky = (bloch_hamiltonian(kx, ky + step, params) - bloch_hamiltonian(kx, ky - step, params)) / (2.0 * step)
    error_kx = float(np.max(np.abs(d_kx - finite_kx)))
    error_ky = float(np.max(np.abs(d_ky - finite_ky)))
    print(f'  dH/dkx finite-difference maximum error = {error_kx:.3e}')
    print(f'  dH/dky finite-difference maximum error = {error_ky:.3e}')
    print('Stage 1 checks passed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
