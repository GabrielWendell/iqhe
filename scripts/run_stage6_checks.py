"""Run Stage-6 chiral-dynamics validation checks.

Run from the repository root:

    python scripts/run_stage6_checks.py
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path
from typing import Literal, cast

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from qhe.dynamics import DynamicsConfig, analyze_chiral_dynamics
from qhe.models import HarperHofstadterParameters

DEFAULT_CONFIG = ROOT / "configs" / "dynamics_validation_phi_1_3.toml"

GapSelector = Literal[0, 1]
EdgeSide = Literal["left", "right", "bottom", "top"]
_GAP_SELECTORS: tuple[GapSelector, ...] = (0, 1)
_EDGE_SIDES: tuple[EdgeSide, ...] = ("left", "right", "bottom", "top")


def _gap_selector(value: object) -> GapSelector:
    """Parse and narrow a TOML value to a valid Stage-6 bulk-gap selector."""
    if isinstance(value, bool):
        raise TypeError("gap_index must be an integer selector, not a boolean.")
    if isinstance(value, int):
        gap_index = value
    elif isinstance(value, str):
        gap_index = int(value.strip())
    else:
        raise TypeError(
            f"gap_index must be an integer or integer-like string; got {type(value).__name__}."
        )

    if gap_index not in _GAP_SELECTORS:
        valid = ", ".join(str(item) for item in _GAP_SELECTORS)
        raise ValueError(f"Unsupported gap_index {gap_index!r}; expected one of: {valid}.")
    return cast(GapSelector, gap_index)


def _edge_side(value: object) -> EdgeSide:
    """Parse and narrow a TOML value to a valid boundary side literal."""
    side = str(value).strip().lower()
    if side not in _EDGE_SIDES:
        valid = ", ".join(_EDGE_SIDES)
        raise ValueError(f"Unsupported side {side!r}; expected one of: {valid}.")
    return cast(EdgeSide, side)


def _load_config(path: Path) -> tuple[DynamicsConfig, dict[str, float]]:
    with path.open("rb") as handle:
        document = tomllib.load(handle)
    model = document["model"]
    dynamics = document["dynamics"]
    bulk = document["bulk_boundary"]
    config = DynamicsConfig(
        parameters=HarperHofstadterParameters(
            p=int(model["p"]),
            q=int(model["q"]),
            tx=float(model["tx"]),
            ty=float(model["ty"]),
            lattice_spacing=float(model["lattice_spacing"]),
        ),
        gap_index=_gap_selector(dynamics["gap_index"]),
        side=_edge_side(dynamics["side"]),
        lx=int(dynamics["lx"]),
        ly=int(dynamics["ly"]),
        edge_width=int(dynamics["edge_width"]),
        sigma_transverse=float(dynamics["sigma_transverse"]),
        sigma_longitudinal=float(dynamics["sigma_longitudinal"]),
        center_longitudinal=float(dynamics["center_longitudinal"]),
        offset_from_boundary=float(dynamics["offset_from_boundary"]),
        time_final=float(dynamics["time_final"]),
        n_times=int(dynamics["n_times"]),
        fit_until=float(dynamics["fit_until"]),
        minimum_side_participation=float(dynamics["minimum_side_participation"]),
        defect_factor=float(dynamics["defect_factor"]),
        hbar=float(dynamics["hbar"]),
        bulk_nkx=int(bulk["bulk_nkx"]),
        ribbon_lx=int(bulk["ribbon_lx"]),
        ribbon_nky=int(bulk["ribbon_nky"]),
        ribbon_edge_threshold=float(bulk["ribbon_edge_threshold"]),
    )
    acceptance = {key: float(value) for key, value in document["acceptance"].items()}
    return config, acceptance


def _check(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config, acceptance = _load_config(args.config)
    analysis = analyze_chiral_dynamics(config)

    failures: list[str] = []
    max_norm = max(analysis.clean.norms.max_deviation, analysis.defect.norms.max_deviation)
    _check(
        max_norm <= acceptance["max_norm_deviation"],
        f"Norm deviation too large: {max_norm:.3e}.",
        failures,
    )
    _check(
        analysis.clean.initial_edge_probability
        >= acceptance["minimum_initial_edge_probability"],
        "Initial edge probability is below the Stage-6 threshold: "
        f"{analysis.clean.initial_edge_probability:.6f}.",
        failures,
    )
    _check(
        analysis.clean.mean_edge_probability
        >= acceptance["minimum_mean_clean_edge_probability"],
        f"Clean mean edge probability too low: {analysis.clean.mean_edge_probability:.6f}.",
        failures,
    )
    _check(
        analysis.defect.mean_edge_probability
        >= acceptance["minimum_mean_defect_edge_probability"],
        f"Defect mean edge probability too low: {analysis.defect.mean_edge_probability:.6f}.",
        failures,
    )
    _check(
        analysis.relative_velocity_error <= acceptance["maximum_relative_velocity_error"],
        "Clean packet velocity disagrees with the ribbon group velocity: "
        f"relative error={analysis.relative_velocity_error:.3f}.",
        failures,
    )
    _check(
        analysis.defect_relative_velocity_error
        <= acceptance["maximum_defect_relative_velocity_error"],
        "Defect packet velocity disagrees too strongly with the ribbon group velocity: "
        f"relative error={analysis.defect_relative_velocity_error:.3f}.",
        failures,
    )
    _check(
        analysis.clean.side_current_initial * analysis.group_velocity > 0.0,
        "Initial side-current sign does not agree with the selected branch velocity.",
        failures,
    )

    print("Stage-6 chiral-dynamics validation")
    print(f"Model: phi = {config.parameters.p}/{config.parameters.q}, tx={config.parameters.tx:g}, ty={config.parameters.ty:g}")
    print(f"Open lattice: Lx = {config.lx}, Ly = {config.ly}, edge width = {config.edge_width}")
    print(
        "Selected branch: "
        f"gap = {config.gap_index + 1}, side = {config.side}, ky={analysis.crossing.ky:.6f}, "
        f"v_g = {analysis.group_velocity:.6f}"
    )
    print(f"Weak-link defect: side = {analysis.weak_link.side}, position = {analysis.weak_link.position}, factor = {analysis.weak_link.factor:g}")
    print()
    print("quantity                         | clean        | defect")
    print("---------------------------------+--------------+--------------")
    print(f"selected edge states             | {analysis.clean.selected_state_count:12d} | {analysis.defect.selected_state_count:12d}")
    print(f"max norm deviation               | {analysis.clean.norms.max_deviation:12.3e} | {analysis.defect.norms.max_deviation:12.3e}")
    print(f"initial edge probability         | {analysis.clean.initial_edge_probability:12.6f} | {analysis.defect.initial_edge_probability:12.6f}")
    print(f"mean edge probability            | {analysis.clean.mean_edge_probability:12.6f} | {analysis.defect.mean_edge_probability:12.6f}")
    print(f"packet velocity                  | {analysis.clean.velocity_fit.velocity:12.6f} | {analysis.defect.velocity_fit.velocity:12.6f}")
    print(f"relative velocity error          | {analysis.relative_velocity_error:12.6f} | {analysis.defect_relative_velocity_error:12.6f}")
    print(f"initial side-current indicator   | {analysis.clean.side_current_initial:12.6f} | {analysis.defect.side_current_initial:12.6f}")

    if failures:
        print("\nStage-6 acceptance checks failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("\nStage-6 chiral-dynamics acceptance checks: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
