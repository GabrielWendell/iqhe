"""Baseline import and metadata checks for the Stage-0 package."""

from qhe import __version__


def test_package_exposes_version() -> None:
    assert __version__ == "0.1.0"
