"""Tests for ``pyduck_ona_viz.hierarchy_viz``."""

from __future__ import annotations

import matplotlib
import matplotlib.figure as mfigure
import pandas as pd
import pytest

matplotlib.use("Agg")

from pyduck_ona_viz.hierarchy_viz import hierarchy_depth_heatmap


@pytest.fixture
def wide_hierarchy() -> pd.DataFrame:
    n = 8
    return pd.DataFrame(
        {
            "employee_id": [f"E{i}" for i in range(n)],
            "Level_1": [None] + [f"X{i % 2}" for i in range(n - 1)],
            "Level_2": [None, None] + [f"X{i % 4}" for i in range(n - 2)],
            "Level_3": [None] * 3 + [f"X{i % 8}" for i in range(n - 3)],
        }
    )


@pytest.fixture
def metadata(wide_hierarchy: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "employee_id": wide_hierarchy["employee_id"],
            "name": [f"Person-{eid}" for eid in wide_hierarchy["employee_id"]],
        }
    )


# ---------------------------------------------------------------------------
# hierarchy_depth_heatmap
# ---------------------------------------------------------------------------


def test_hierarchy_depth_heatmap_returns_figure(
    wide_hierarchy: pd.DataFrame,
) -> None:
    fig = hierarchy_depth_heatmap(wide_hierarchy)
    assert isinstance(fig, mfigure.Figure)


def test_hierarchy_depth_heatmap_with_metadata(
    wide_hierarchy: pd.DataFrame, metadata: pd.DataFrame
) -> None:
    fig = hierarchy_depth_heatmap(wide_hierarchy, metadata=metadata, annotate=True)
    assert isinstance(fig, mfigure.Figure)


def test_hierarchy_depth_heatmap_max_levels(
    wide_hierarchy: pd.DataFrame,
) -> None:
    fig = hierarchy_depth_heatmap(wide_hierarchy, max_levels=2)
    assert isinstance(fig, mfigure.Figure)


def test_hierarchy_depth_heatmap_single_row() -> None:
    df = pd.DataFrame({"employee_id": ["E0"], "Level_1": [None], "Level_2": [None]})
    fig = hierarchy_depth_heatmap(df)
    assert isinstance(fig, mfigure.Figure)


def test_hierarchy_depth_heatmap_missing_employee_col_raises() -> None:
    df = pd.DataFrame({"Level_1": ["A"]})
    with pytest.raises(KeyError):
        hierarchy_depth_heatmap(df)


def test_hierarchy_depth_heatmap_missing_level_columns_raises() -> None:
    df = pd.DataFrame({"employee_id": ["A", "B"]})
    with pytest.raises(ValueError, match="No columns starting with"):
        hierarchy_depth_heatmap(df)


def test_hierarchy_depth_heatmap_non_dataframe_raises() -> None:
    with pytest.raises(TypeError):
        hierarchy_depth_heatmap([1, 2, 3])  # type: ignore[arg-type]


def test_hierarchy_depth_heatmap_all_nan_level() -> None:
    df = pd.DataFrame(
        {
            "employee_id": ["E0", "E1"],
            "Level_1": [None, None],
            "Level_2": [None, None],
        }
    )
    fig = hierarchy_depth_heatmap(df)
    assert isinstance(fig, mfigure.Figure)
