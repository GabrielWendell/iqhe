"""Run Stage-2 bulk-topology acceptance checks.

Run from the repository root after installing the package in editable mode:

    python scripts/run_stage2_checks.py
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

import numpy as np

from qhe.models import HarperHofstadterParameters
from qhe.topology import harper_hofstadter_convergence

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "topology_validation_phi_1_3.toml"


def _format_vector(values: np.ndarray, *, digits: int = 6) -> str:
    return "[" + ", ".join(f"{float(value):.{digits}f}" for value in values) + "]"


def main() -> int:
    with CONFIG_PATH.open("rb") as handle:
        config = tomllib.load(handle)

    model = config["model"]
    validation = config["validation"]
    expected = np.asarray(config["expected"]["chern_numbers"], dtype=float)
    mesh_sizes = tuple(int(size) for size in config["mesh"]["resolutions"])

    parameters = HarperHofstadterParameters(
        p=int(model["p"]),
        q=int(model["q"]),
        tx=float(model["tx"]),
        ty=float(model["ty"]),
        lattice_spacing=float(model["lattice_spacing"]),
    )
    result = harper_hofstadter_convergence(
        parameters,
        mesh_sizes=mesh_sizes,
        overlap_floor=float(validation["overlap_floor"]),
        degeneracy_tolerance=float(validation["degeneracy_tolerance"]),
    )

    print("Stage-2 topology validation")
    print(f"Model: phi={parameters.p}/{parameters.q}, tx={parameters.tx:g}, ty={parameters.ty:g}")
    print(f"Expected Chern sequence: {_format_vector(expected, digits=0)}")
    print()
    print("mesh | FHS Chern                  | Kubo Chern                 | min direct gap")
    print("-----+----------------------------+-----------------------------+---------------")
    for index, mesh_size in enumerate(result.mesh_sizes):
        minimum_gap = float(np.min(result.minimum_direct_gaps[index]))
        print(
            f"{int(mesh_size):4d} | {_format_vector(result.fhs_chern_numbers[index])} | "
            f"{_format_vector(result.kubo_chern_numbers[index])} | {minimum_gap:.8f}"
        )

    print()
    print("final-mesh FHS/Kubo density residual norms")
    print(f"L2:   {_format_vector(result.l2_errors[-1])}")
    print(f"Linf: {_format_vector(result.linf_errors[-1])}")

    fhs_error = float(np.max(np.abs(result.fhs_chern_numbers - expected)))
    kubo_error = float(np.max(np.abs(result.kubo_chern_numbers[-1] - expected)))
    minimum_gap = float(np.min(result.minimum_direct_gaps))
    l2_decreases = bool(np.all(result.l2_errors[-1] < result.l2_errors[0]))
    linf_decreases = bool(np.all(result.linf_errors[-1] < result.linf_errors[0]))

    failures: list[str] = []
    if fhs_error > float(validation["fhs_chern_atol"]):
        failures.append(f"FHS Chern error {fhs_error:.3e} exceeded tolerance.")
    if kubo_error > float(validation["kubo_chern_atol_final_mesh"]):
        failures.append(f"Final-mesh Kubo Chern error {kubo_error:.3e} exceeded tolerance.")
    if minimum_gap <= float(validation["minimum_direct_gap_floor"]):
        failures.append(f"Minimum direct gap {minimum_gap:.3e} was not safely positive.")
    if not l2_decreases:
        failures.append("FHS/Kubo L2 residuals did not decrease at every mesh-refinement step.")
    if not linf_decreases:
        failures.append("FHS/Kubo Linf residuals did not decrease at every mesh-refinement step.")

    if failures:
        print()
        print("Stage-2 checks failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print()
    print("Stage-2 topology acceptance checks: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
