"""Import and metadata checks for the Stage-3 package."""

from qhe import __version__


def test_package_exposes_version() -> None:
    assert __version__ == "0.5.0"
