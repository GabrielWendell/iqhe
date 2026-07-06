"""Shared visualization helpers and reproducible figure builders."""

from qhe.viz.edge import plot_bulk_boundary_spectrum, plot_crossing_profiles, plot_ribbon_spectrum
from qhe.viz.manuscript import plot_ribbon_bulk_boundary_figure
from qhe.viz.schematics import plot_conceptual_roadmap, plot_fhs_plaquette
from qhe.viz.topology import (
    plot_fhs_kubo_validation,
    plot_hofstadter_bulk_bands,
    plot_massive_dirac_warmup,
)

__all__ = [
    "plot_bulk_boundary_spectrum",
    "plot_conceptual_roadmap",
    "plot_crossing_profiles",
    "plot_fhs_kubo_validation",
    "plot_fhs_plaquette",
    "plot_hofstadter_bulk_bands",
    "plot_massive_dirac_warmup",
    "plot_ribbon_bulk_boundary_figure",
    "plot_ribbon_spectrum",
]
