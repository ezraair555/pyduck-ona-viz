"""Tests for ``pyduck_ona_viz.org_chart``."""

from __future__ import annotations

import time

import matplotlib
import matplotlib.figure as mfigure
import numpy as np
import pandas as pd
import pytest

matplotlib.use("Agg")

from pyduck_ona_viz.org_chart import org_chart_tree, reporting_chain_walk


@pytest.fixture
def hierarchy() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "employee_id": ["CEO", "VP1", "VP2", "M1", "M2", "IC1"],
            "supervisor_id": [None, "CEO", "CEO", "VP1", "VP2", "M1"],
        }
    )


@pytest.fixture
def metadata(hierarchy: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "employee_id": hierarchy["employee_id"],
            "name": [f"Person-{eid}" for eid in hierarchy["employee_id"]],
            "title": ["CEO", "VP", "VP", "Manager", "Manager", "IC"],
            "department": ["Exec", "Eng", "Sales", "Eng", "Sales", "Eng"],
            "level": ["L5", "L4", "L4", "L3", "L3", "L1"],
        }
    )


# ---------------------------------------------------------------------------
# org_chart_tree
# ---------------------------------------------------------------------------


def test_org_chart_tree_returns_html(hierarchy: pd.DataFrame) -> None:
    html = org_chart_tree(hierarchy)
    assert isinstance(html, str)
    assert "<!DOCTYPE html>" in html
    assert "d3" in html.lower()


@pytest.mark.parametrize("color_by", ["department", "level", None])
def test_org_chart_tree_color_by_options(
    hierarchy: pd.DataFrame, metadata: pd.DataFrame, color_by: str | None
) -> None:
    html = org_chart_tree(hierarchy, metadata=metadata, color_by=color_by)
    assert isinstance(html, str)
    assert "<!DOCTYPE html>" in html


def test_org_chart_tree_single_root() -> None:
    df = pd.DataFrame({"employee_id": ["A"], "supervisor_id": [None]})
    html = org_chart_tree(df)
    assert isinstance(html, str)


def test_org_chart_tree_multi_root_uses_first_root(
    hierarchy: pd.DataFrame,
) -> None:
    # Add a second disconnected root
    extra = pd.DataFrame({"employee_id": ["ROOT2", "X1"], "supervisor_id": [None, "ROOT2"]})
    df = pd.concat([hierarchy, extra], ignore_index=True)
    html = org_chart_tree(df)
    assert isinstance(html, str)


def test_org_chart_tree_root_id_not_found_raises(
    hierarchy: pd.DataFrame,
) -> None:
    with pytest.raises(ValueError, match="root_id 'missing' not found"):
        org_chart_tree(hierarchy, root_id="missing")


def test_org_chart_tree_explicit_root_id(hierarchy: pd.DataFrame) -> None:
    html = org_chart_tree(hierarchy, root_id="VP1")
    assert isinstance(html, str)


def test_org_chart_tree_xss_payload_in_metadata_is_escaped(
    hierarchy: pd.DataFrame,
) -> None:
    bad_name = "<script>alert('xss')</script>"
    meta = pd.DataFrame(
        {
            "employee_id": ["CEO"],
            "name": [bad_name],
            "title": [bad_name],
            "department": [bad_name],
        }
    )
    html = org_chart_tree(hierarchy, metadata=meta, color_by="department")
    assert bad_name not in html
    # Ensure the literal text is present but HTML-escaped
    assert "&lt;script&gt;" in html


def test_org_chart_tree_xss_in_title_is_escaped(hierarchy: pd.DataFrame) -> None:
    bad_title = "<script>alert('title')</script>"
    html = org_chart_tree(hierarchy, title=bad_title)
    assert bad_title not in html


def test_org_chart_tree_rejects_duplicate_employee_ids() -> None:
    df = pd.DataFrame(
        {
            "employee_id": ["A", "A", "B"],
            "supervisor_id": [None, "A", "A"],
        }
    )
    with pytest.raises(ValueError, match="Duplicate employee IDs"):
        org_chart_tree(df)


def test_org_chart_tree_rejects_missing_columns() -> None:
    df = pd.DataFrame({"foo": [1, 2]})
    with pytest.raises(KeyError):
        org_chart_tree(df)


def test_org_chart_tree_rejects_non_dataframe() -> None:
    with pytest.raises(TypeError):
        org_chart_tree([1, 2, 3])  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# reporting_chain_walk
# ---------------------------------------------------------------------------


def test_reporting_chain_walk_returns_figure(
    hierarchy: pd.DataFrame,
) -> None:
    fig = reporting_chain_walk(hierarchy, "IC1")
    assert isinstance(fig, mfigure.Figure)
    assert len(fig.axes) == 1


def test_reporting_chain_walk_with_metadata(
    hierarchy: pd.DataFrame, metadata: pd.DataFrame
) -> None:
    fig = reporting_chain_walk(hierarchy, "IC1", metadata=metadata)
    assert isinstance(fig, mfigure.Figure)


@pytest.mark.parametrize("size", [3, 5, 10])
def test_reporting_chain_walk_detects_cycle(size: int) -> None:
    ids = [f"E{i}" for i in range(size)]
    supervisors = [ids[(i + 1) % size] for i in range(size)]
    df = pd.DataFrame({"employee_id": ids, "supervisor_id": supervisors})
    with pytest.raises(ValueError, match="Cycle detected"):
        reporting_chain_walk(df, ids[0])


def test_reporting_chain_walk_top_of_org(hierarchy: pd.DataFrame) -> None:
    fig = reporting_chain_walk(hierarchy, "CEO")
    assert isinstance(fig, mfigure.Figure)


def test_reporting_chain_walk_missing_employee_id() -> None:
    df = pd.DataFrame({"employee_id": ["A", "B"], "supervisor_id": [None, "A"]})
    # The walk starts from the given id and continues until a root or cycle.
    # An unknown starting id produces an empty chain (only the id itself),
    # which is currently accepted.
    fig = reporting_chain_walk(df, "Z")
    assert isinstance(fig, mfigure.Figure)


# ---------------------------------------------------------------------------
# Performance
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_org_chart_tree_10k_rows_within_five_seconds() -> None:
    n = 10_000
    rng = np.random.default_rng(42)
    ids = [f"E{i:05d}" for i in range(n)]
    sups: list[str | None] = [None]
    for i in range(1, n):
        parent_idx = rng.integers(0, i)
        sups.append(ids[parent_idx])
    df = pd.DataFrame({"employee_id": ids, "supervisor_id": sups})
    start = time.perf_counter()
    html = org_chart_tree(df)
    elapsed = time.perf_counter() - start
    assert isinstance(html, str)
    assert elapsed < 5.0
