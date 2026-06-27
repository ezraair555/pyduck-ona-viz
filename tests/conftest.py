"""Shared pytest configuration for pyduck-ona-viz tests."""

from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import pytest

matplotlib.use("Agg")
matplotlib.rcParams["figure.max_open_warning"] = 0


@pytest.fixture(autouse=True)
def _close_figures():
    """Close any matplotlib figures after each test to avoid warnings."""
    yield
    plt.close("all")
