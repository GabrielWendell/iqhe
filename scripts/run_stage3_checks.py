"""Run deterministic Stage-3 edge-physics acceptance checks.

Run from the repository root:

    python scripts/run_stage3_checks.py
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

import numpy as np

from qhe.boundary import analyze_bulk_boundary_correspondence
from qhe.models import HarperHofstadterParameters

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "edge_validation_phi_1_3.toml"


def _format_array(values: np.ndarray | list[int]) -> str:
    array = np.asarray(values)
    return "[" + ", ".join(str(int(value)) for value in array) + "]"


def main() -> int:
    with CONFIG_PATH.open("rb") as handle:
        config = tomllib.load(handle)

    model = config["model"]
    bulk = config["bulk"]
    ribbon_config = config["ribbon"]
    expected = config["expected"]
    validation = config["validation"]

    params = HarperHofstadterParameters(
        p=int(model["p"]),
        q=int(model["q"]),
        tx=float(model["tx"]),
        ty=float(model["ty"]),
        lattice_spacing=float(model["lattice_spacing"]),
    )
    threshold = float(validation["edge_participation_threshold"])
    analysis = analyze_bulk_boundary_correspondence(
        params,
        bulk_nkx=int(bulk["nkx"]),
        bulk_nky=int(bulk["nky"]),
        ribbon_lx=int(ribbon_config["lx"]),
        ribbon_nky=int(ribbon_config["nky"]),
        edge_width=int(ribbon_config["edge_width"]),
        edge_threshold=threshold,
        side_margin=float(validation["side_margin"]),
    )

    band_chern = np.rint(analysis.topology.fhs.chern_numbers).astype(int)
    gap_chern = np.asarray(
        [summary.gap.gap_chern_number for summary in analysis.crossing_summaries]
    )
    left_counts = np.asarray(
        [summary.left_oriented_crossing_count for summary in analysis.crossing_summaries],
        dtype=int,
    )
    right_counts = np.asarray(
        [summary.right_oriented_crossing_count for summary in analysis.crossing_summaries],
        dtype=int,
    )
    minimum_gap = min(summary.gap.width for summary in analysis.crossing_summaries)

    print("Stage-3 edge-physics validation")
    print(f"Model: phi={params.p}/{params.q}, tx={params.tx:g}, ty={params.ty:g}")
    print(
        "Ribbon: "
        f"Lx={analysis.ribbon.lx}, N_ky={analysis.ribbon.nky}, "
        f"edge width={analysis.ribbon.edge_masks.width}"
    )
    print(f"FHS band Chern sequence: {_format_array(band_chern)}")
    print()
    print(
        "gap | interval                  | C_gap | left crossings | right crossings | "
        "edge crossings"
    )
    print(
        "----+---------------------------+-------+----------------+-----------------+"
        "---------------"
    )
    for summary in analysis.crossing_summaries:
        crossing_count = len(summary.crossings)
        print(
            f" {summary.gap.index + 1:>2d} | "
            f"[{summary.gap.lower_edge: .6f}, {summary.gap.upper_edge: .6f}] | "
            f" {summary.gap.gap_chern_number:>+3d}  | "
            f" {summary.left_oriented_crossing_count:>+6d}         | "
            f" {summary.right_oriented_crossing_count:>+7d}          | "
            f" {crossing_count:>5d}"
        )

    failures: list[str] = []
    if not np.array_equal(band_chern, np.asarray(expected["band_chern_numbers"], dtype=int)):
        failures.append("FHS band Chern sequence disagrees with the Stage-2 frozen result.")
    if not np.array_equal(gap_chern, np.asarray(expected["gap_chern_numbers"], dtype=int)):
        failures.append("Gap Chern numbers disagree with the expected cumulative sequence.")
    expected_left = np.asarray(expected["left_oriented_crossing_counts"], dtype=int)
    if not np.array_equal(left_counts, expected_left):
        failures.append(
            "Left-edge oriented crossing counts disagree with the frozen convention target."
        )
    expected_right = np.asarray(expected["right_oriented_crossing_counts"], dtype=int)
    if not np.array_equal(right_counts, expected_right):
        failures.append(
            "Right-edge oriented crossing counts disagree with the frozen convention target."
        )
    if minimum_gap <= float(validation["minimum_bulk_gap_floor"]):
        failures.append(f"Minimum global bulk gap {minimum_gap:.3e} is not safely positive.")

    for summary in analysis.crossing_summaries:
        if not summary.left_crossings or not summary.right_crossings:
            failures.append(
                f"Gap {summary.gap.index + 1} does not show one localized crossing on each edge."
            )
        if summary.ambiguous_crossings:
            failures.append(
                f"Gap {summary.gap.index + 1} contains an ambiguously side-assigned crossing."
            )
        if any(crossing.edge_participation < threshold for crossing in summary.crossings):
            failures.append(
                f"Gap {summary.gap.index + 1} contains a crossing below the edge threshold."
            )

    if failures:
        print()
        print("Stage-3 checks failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print()
    print("Stage-3 edge-physics acceptance checks: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
