"""Tests for Stage-0 validation primitives."""

import numpy as np
import pytest

from qhe.exceptions import ValidationError
from qhe.validation import assert_hermitian


def test_assert_hermitian_accepts_hermitian_matrix() -> None:
    matrix = np.array([[1.0, 1.0j], [-1.0j, 2.0]])
    assert_hermitian(matrix)


def test_assert_hermitian_rejects_nonhermitian_matrix() -> None:
    matrix = np.array([[0.0, 1.0], [0.0, 0.0]])
    with pytest.raises(ValidationError, match="not Hermitian"):
        assert_hermitian(matrix)
