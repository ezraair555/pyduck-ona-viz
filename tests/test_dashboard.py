"""Tests for ``pyduck_ona_viz.dashboard``."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from pyduck_ona_viz.dashboard import (
    _kpi_cards_html,
    _panel_card,
    _wrap_html,
    summary_dashboard,
)


@pytest.fixture
def stats() -> pd.DataFrame:
    rng = np.random.default_rng(9)
    return pd.DataFrame(
        {
            "employee_id": [f"M{i:02d}" for i in range(10)],
            "direct_reports": rng.integers(0, 15, 10),
            "total_reports": rng.integers(1, 50, 10),
            "levels_below": rng.integers(0, 5, 10),
        }
    )


@pytest.fixture
def betweenness() -> pd.DataFrame:
    return pd.DataFrame({"node_id": ["A", "B", "C"], "betweenness": [0.5, 0.3, 0.2]})


@pytest.fixture
def pagerank() -> pd.DataFrame:
    return pd.DataFrame({"node_id": ["A", "B", "C"], "pagerank": [0.4, 0.35, 0.25]})


@pytest.fixture
def diversity() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "group": ["F", "M", "NB"],
            "count": [120, 175, 5],
        }
    )


@pytest.fixture
def attrition() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "department": ["Eng"] * 3 + ["Sales"] * 3,
            "job_level": ["IC", "Mgr", "Dir"] * 2,
            "rate": [0.10, 0.15, 0.22, 0.18, 0.20, 0.28],
            "count": [20, 10, 5, 25, 8, 3],
        }
    )


# ---------------------------------------------------------------------------
# summary_dashboard
# ---------------------------------------------------------------------------


def test_summary_dashboard_with_all_optional_frames(
    stats: pd.DataFrame,
    betweenness: pd.DataFrame,
    pagerank: pd.DataFrame,
    diversity: pd.DataFrame,
    attrition: pd.DataFrame,
) -> None:
    html = summary_dashboard(
        stats,
        betweenness=betweenness,
        pagerank=pagerank,
        diversity=diversity,
        attrition=attrition,
    )
    assert isinstance(html, str)
    assert "<!DOCTYPE html>" in html
    assert "Plotly" in html or "plotly" in html.lower()


def test_summary_dashboard_no_optional_frames(stats: pd.DataFrame) -> None:
    html = summary_dashboard(stats)
    assert isinstance(html, str)
    assert "Headcount" in html
    assert "Managers" in html


def test_summary_dashboard_empty_optional_frames(stats: pd.DataFrame) -> None:
    empty = pd.DataFrame()
    html = summary_dashboard(
        stats,
        betweenness=empty,
        pagerank=empty,
        diversity=empty,
        attrition=empty,
    )
    assert isinstance(html, str)


def test_summary_dashboard_xss_title_is_escaped(stats: pd.DataFrame) -> None:
    bad = "<script>alert('dash')</script>"
    html = summary_dashboard(stats, title=bad, subtitle=bad)
    assert bad not in html
    assert "&lt;script&gt;" in html


def test_summary_dashboard_non_dataframe_raises() -> None:
    with pytest.raises((TypeError, AttributeError)):
        summary_dashboard([1, 2, 3])  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------


def test_panel_card_escapes_title_and_subtitle() -> None:
    bad = "<script>alert('card')</script>"
    html = _panel_card(bad, bad, "<div>plot</div>")
    assert bad not in html
    assert "&lt;script&gt;" in html


def test_kpi_cards_html_escapes_values() -> None:
    bad = "<script>alert('kpi')</script>"
    html = _kpi_cards_html([("Label", bad)])
    assert bad not in html
    assert "&lt;script&gt;" in html


def test_wrap_html_escapes_title_and_subtitle() -> None:
    bad = "<script>alert('wrap')</script>"
    html = _wrap_html(bad, bad, [])
    assert bad not in html
    assert "&lt;script&gt;" in html


def test_wrap_html_returns_doctype() -> None:
    html = _wrap_html("T", "S", [])
    assert "<!DOCTYPE html>" in html
    assert "T" in html
    assert "S" in html
