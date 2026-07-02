"""Stage-3 bulk-boundary correspondence regression tests."""

import numpy as np

from qhe.boundary import analyze_bulk_boundary_correspondence, gap_chern_numbers
from qhe.models import HarperHofstadterParameters


def test_gap_chern_numbers_are_cumulative() -> None:
    assert np.array_equal(gap_chern_numbers(np.array([-1.0, 2.0, -1.0])), np.array([-1, 1]))


def test_phi_one_third_ribbon_has_side_resolved_chiral_crossings() -> None:
    analysis = analyze_bulk_boundary_correspondence(
        HarperHofstadterParameters(p=1, q=3, tx=1.0, ty=1.0),
        bulk_nkx=21,
        bulk_nky=21,
        ribbon_lx=36,
        ribbon_nky=121,
        edge_width=3,
        edge_threshold=0.60,
    )
    assert [gap.gap_chern_number for gap in analysis.gaps] == [-1, 1]
    left_counts = [summary.left_oriented_crossing_count for summary in analysis.crossing_summaries]
    assert left_counts == [-1, 1]
    right_counts = [
        summary.right_oriented_crossing_count for summary in analysis.crossing_summaries
    ]
    assert right_counts == [1, -1]
    for summary in analysis.crossing_summaries:
        assert summary.gap.width > 0.0
        assert len(summary.left_crossings) == 1
        assert len(summary.right_crossings) == 1
        assert not summary.ambiguous_crossings
        assert all(crossing.edge_participation >= 0.60 for crossing in summary.crossings)
