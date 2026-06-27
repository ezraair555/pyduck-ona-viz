"""Tests for ``pyduck_ona_viz.hr_viz``."""

from __future__ import annotations

import matplotlib
import matplotlib.figure as mfigure
import numpy as np
import pandas as pd
import pytest

matplotlib.use("Agg")

from pyduck_ona_viz.hr_viz import attrition_heatmap, compensation_equity

# ---------------------------------------------------------------------------
# attrition_heatmap
# ---------------------------------------------------------------------------


def _make_attrition_raw(n_per_cell: int = 10) -> pd.DataFrame:
    rng = np.random.default_rng(5)
    rows = []
    for dept in ["Eng", "Sales", "Marketing"]:
        for level in ["IC", "Mgr", "Dir"]:
            for _ in range(n_per_cell):
                rows.append(
                    {
                        "department": dept,
                        "job_level": level,
                        "attrition": int(rng.random() > 0.8),
                    }
                )
    return pd.DataFrame(rows)


def _make_attrition_aggregated() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "department": ["Eng", "Eng", "Sales", "Sales"],
            "job_level": ["IC", "Mgr", "IC", "Mgr"],
            "rate": [0.10, 0.15, 0.20, 0.25],
            "count": [20, 10, 30, 8],
        }
    )


def test_attrition_heatmap_raw_frame() -> None:
    df = _make_attrition_raw()
    fig = attrition_heatmap(df)
    assert isinstance(fig, mfigure.Figure)


def test_attrition_heatmap_pre_aggregated_frame() -> None:
    df = _make_attrition_aggregated()
    fig = attrition_heatmap(df, value_col="rate", count_col="count")
    assert isinstance(fig, mfigure.Figure)


def test_attrition_heatmap_missing_value_column_raises() -> None:
    df = _make_attrition_aggregated().drop(columns=["rate"])
    with pytest.raises(KeyError):
        attrition_heatmap(df, value_col="rate", count_col="count")


def test_attrition_heatmap_missing_required_columns_raises() -> None:
    df = pd.DataFrame({"foo": [1, 2, 3]})
    with pytest.raises(KeyError):
        attrition_heatmap(df)


def test_attrition_heatmap_non_dataframe_raises() -> None:
    with pytest.raises(TypeError):
        attrition_heatmap([1, 2, 3])  # type: ignore[arg-type]


def test_attrition_heatmap_empty_after_groupby() -> None:
    df = pd.DataFrame(
        {
            "department": pd.Series([], dtype=str),
            "job_level": pd.Series([], dtype=str),
            "attrition": pd.Series([], dtype=int),
        }
    )
    with pytest.warns(UserWarning, match="transformation singular"):
        fig = attrition_heatmap(df)
    assert isinstance(fig, mfigure.Figure)


# ---------------------------------------------------------------------------
# compensation_equity
# ---------------------------------------------------------------------------


def _make_compensation(n: int = 50) -> pd.DataFrame:
    rng = np.random.default_rng(6)
    return pd.DataFrame(
        {
            "employee_id": [f"E{i:04d}" for i in range(n)],
            "tenure_years": rng.uniform(0, 20, n),
            "salary": rng.normal(120_000, 25_000, n),
            "gender": rng.choice(["F", "M"], n),
        }
    )


def test_compensation_equity_returns_figure() -> None:
    df = _make_compensation()
    fig = compensation_equity(df, group_col="gender")
    assert isinstance(fig, mfigure.Figure)


def test_compensation_equity_without_group() -> None:
    df = _make_compensation()
    fig = compensation_equity(df, group_col=None)
    assert isinstance(fig, mfigure.Figure)


def test_compensation_equity_single_row() -> None:
    df = pd.DataFrame(
        {
            "tenure_years": [5.0],
            "salary": [100_000.0],
        }
    )
    fig = compensation_equity(df)
    assert isinstance(fig, mfigure.Figure)


def test_compensation_equity_missing_column_raises() -> None:
    df = pd.DataFrame({"foo": [1, 2, 3]})
    with pytest.raises(KeyError):
        compensation_equity(df)


def test_compensation_equity_non_dataframe_raises() -> None:
    with pytest.raises(TypeError):
        compensation_equity([1, 2, 3])  # type: ignore[arg-type]


def test_compensation_equity_with_metadata() -> None:
    df = _make_compensation(10)
    meta = pd.DataFrame(
        {
            "employee_id": df["employee_id"],
            "name": [f"Person-{i}" for i in range(len(df))],
        }
    )
    fig = compensation_equity(df, metadata=meta, group_col="gender")
    assert isinstance(fig, mfigure.Figure)


def test_compensation_equity_two_groups_pay_gap_annotation() -> None:
    df = pd.DataFrame(
        {
            "tenure_years": [1.0, 2.0, 3.0, 4.0],
            "salary": [80_000.0, 90_000.0, 110_000.0, 120_000.0],
            "gender": ["F", "F", "M", "M"],
        }
    )
    fig = compensation_equity(df, group_col="gender")
    assert isinstance(fig, mfigure.Figure)
