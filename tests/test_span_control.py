"""Tests for ``pyduck_ona_viz.span_control``."""

from __future__ import annotations

import matplotlib
import matplotlib.figure as mfigure
import numpy as np
import pandas as pd
import pytest

matplotlib.use("Agg")

from pyduck_ona_viz.span_control import span_of_control, span_vs_depth


def _make_stats(n: int = 10) -> pd.DataFrame:
    rng = np.random.default_rng(1)
    return pd.DataFrame(
        {
            "employee_id": [f"E{i:04d}" for i in range(n)],
            "direct_reports": rng.integers(0, 15, n),
            "total_reports": rng.integers(1, 50, n),
            "levels_below": rng.integers(0, 5, n),
        }
    )


# ---------------------------------------------------------------------------
# span_of_control
# ---------------------------------------------------------------------------


def test_span_of_control_returns_figure() -> None:
    df = _make_stats()
    fig = span_of_control(df, top_n=10)
    assert isinstance(fig, mfigure.Figure)


def test_span_of_control_returns_html() -> None:
    df = _make_stats()
    html = span_of_control(df, top_n=10, return_html=True)
    assert isinstance(html, str)
    assert "plotly" in html.lower()


def test_span_of_control_empty_frame() -> None:
    df = pd.DataFrame({"employee_id": [], "direct_reports": []})
    fig = span_of_control(df)
    assert isinstance(fig, mfigure.Figure)


def test_span_of_control_single_manager() -> None:
    df = pd.DataFrame(
        {
            "employee_id": ["M1"],
            "direct_reports": [5],
        }
    )
    fig = span_of_control(df)
    assert isinstance(fig, mfigure.Figure)


@pytest.mark.parametrize("metric_col", ["direct_reports", "total_reports"])
def test_span_of_control_metric_columns(metric_col: str) -> None:
    df = _make_stats()[["employee_id", "direct_reports"]].copy()
    df = df.rename(columns={"direct_reports": metric_col})
    fig = span_of_control(df, metric_col=metric_col, top_n=5)
    assert isinstance(fig, mfigure.Figure)


def test_span_of_control_color_by_department() -> None:
    df = _make_stats()
    meta = pd.DataFrame(
        {
            "employee_id": df["employee_id"],
            "name": [f"Person-{i}" for i in range(len(df))],
            "department": (["Eng", "Sales"] * (len(df) // 2 + 1))[: len(df)],
        }
    )
    fig = span_of_control(df, metadata=meta, color_by_department=True, department_col="department")
    assert isinstance(fig, mfigure.Figure)


def test_span_of_control_missing_column_raises() -> None:
    df = pd.DataFrame({"foo": [1, 2, 3]})
    with pytest.raises(KeyError):
        span_of_control(df)


def test_span_of_control_non_dataframe_raises() -> None:
    with pytest.raises(TypeError):
        span_of_control([1, 2, 3])  # type: ignore[arg-type]


def test_span_of_control_metadata_label_lookup() -> None:
    df = _make_stats(3)
    meta = pd.DataFrame(
        {
            "employee_id": df["employee_id"],
            "name": ["Alice", "Bob", "Carol"],
        }
    )
    fig = span_of_control(df, metadata=meta, top_n=3)
    assert isinstance(fig, mfigure.Figure)


def test_span_of_control_id_col_alias() -> None:
    df = _make_stats().rename(columns={"employee_id": "manager_id"})
    fig = span_of_control(df, id_col="manager_id", top_n=5)
    assert isinstance(fig, mfigure.Figure)


def test_span_of_control_html_xss_payload_is_escaped() -> None:
    df = pd.DataFrame(
        {
            "employee_id": ["<script>alert('xss')</script>"],
            "direct_reports": [5],
        }
    )
    html = span_of_control(df, title="<script>alert('title')</script>", return_html=True)
    assert "<script>alert('xss')</script>" not in html
    assert "<script>alert('title')</script>" not in html


# ---------------------------------------------------------------------------
# span_vs_depth
# ---------------------------------------------------------------------------


def test_span_vs_depth_returns_figure() -> None:
    df = _make_stats()
    fig = span_vs_depth(df)
    assert isinstance(fig, mfigure.Figure)


def test_span_vs_depth_missing_column_raises() -> None:
    df = pd.DataFrame({"employee_id": ["a"], "direct_reports": [1]})
    with pytest.raises(KeyError):
        span_vs_depth(df)


def test_span_vs_depth_single_row() -> None:
    df = pd.DataFrame(
        {
            "employee_id": ["M1"],
            "direct_reports": [5],
            "levels_below": [2],
            "total_reports": [10],
        }
    )
    fig = span_vs_depth(df)
    assert isinstance(fig, mfigure.Figure)


def test_span_vs_depth_with_metadata() -> None:
    df = _make_stats()
    meta = pd.DataFrame(
        {
            "employee_id": df["employee_id"],
            "name": [f"Person-{i}" for i in range(len(df))],
        }
    )
    fig = span_vs_depth(df, metadata=meta)
    assert isinstance(fig, mfigure.Figure)
