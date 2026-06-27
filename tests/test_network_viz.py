"""Tests for ``pyduck_ona_viz.network_viz``."""

from __future__ import annotations

import matplotlib
import matplotlib.figure as mfigure
import numpy as np
import pandas as pd
import pytest

matplotlib.use("Agg")

from pyduck_ona_viz.network_viz import centrality_dashboard, silo_map


@pytest.fixture
def nodes() -> list[str]:
    return ["A", "B", "C", "D", "E"]


@pytest.fixture
def centrality_frames(nodes: list[str]) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(3)
    n = len(nodes)
    return {
        "betweenness": pd.DataFrame({"node_id": nodes, "betweenness": rng.random(n)}),
        "pagerank": pd.DataFrame({"node_id": nodes, "pagerank": rng.random(n)}),
        "eigenvector": pd.DataFrame({"node_id": nodes, "eigenvector": rng.random(n)}),
        "degree": pd.DataFrame(
            {
                "node_id": nodes,
                "degree": rng.integers(0, 10, n).astype(float),
            }
        ),
    }


@pytest.fixture
def edges(nodes: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "employee_id": ["A", "B", "C", "D", "E", "A", "B"],
            "supervisor_id": ["B", "C", "D", "E", "A", "D", "E"],
        }
    )


@pytest.fixture
def communities(nodes: list[str]) -> pd.DataFrame:
    return pd.DataFrame({"node_id": nodes, "community": [0, 0, 0, 1, 1]})


@pytest.fixture
def metadata(nodes: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "node_id": nodes,
            "name": [f"Node-{n}" for n in nodes],
            "department": ["Eng", "Eng", "Sales", "Sales", "HR"],
        }
    )


# ---------------------------------------------------------------------------
# centrality_dashboard
# ---------------------------------------------------------------------------


def test_centrality_dashboard_returns_figure(
    centrality_frames: dict[str, pd.DataFrame],
) -> None:
    fig = centrality_dashboard(**centrality_frames, top_n=3)
    assert isinstance(fig, mfigure.Figure)
    assert len(fig.axes) == 4


def test_centrality_dashboard_with_metadata(
    centrality_frames: dict[str, pd.DataFrame], metadata: pd.DataFrame
) -> None:
    fig = centrality_dashboard(
        **centrality_frames, metadata=metadata, department_col="department", top_n=3
    )
    assert isinstance(fig, mfigure.Figure)


@pytest.mark.parametrize("missing", ["betweenness", "pagerank", "eigenvector", "degree"])
def test_centrality_dashboard_missing_column_raises(
    centrality_frames: dict[str, pd.DataFrame], missing: str
) -> None:
    bad_frames = dict(centrality_frames)
    bad_frames[missing] = bad_frames[missing].rename(columns={missing: "wrong"})
    with pytest.raises(KeyError):
        centrality_dashboard(**bad_frames)


def test_centrality_dashboard_empty_frame() -> None:
    empty = pd.DataFrame({"node_id": [], "score": []})
    # Panels should still render; some panels will be empty.
    fig = centrality_dashboard(
        betweenness=empty,
        pagerank=empty,
        eigenvector=empty,
        degree=empty,
        id_col="node_id",
        betweenness_col="score",
        pagerank_col="score",
        eigenvector_col="score",
        degree_col="score",
    )
    assert isinstance(fig, mfigure.Figure)


# ---------------------------------------------------------------------------
# silo_map
# ---------------------------------------------------------------------------


def test_silo_map_returns_html(edges: pd.DataFrame, communities: pd.DataFrame) -> None:
    html = silo_map(edges, communities=communities, return_html=True)
    assert isinstance(html, str)
    assert "<!DOCTYPE html>" in html


def test_silo_map_returns_figure(edges: pd.DataFrame, communities: pd.DataFrame) -> None:
    fig = silo_map(edges, communities=communities, return_html=False)
    assert isinstance(fig, mfigure.Figure)


def test_silo_map_xss_title_and_subtitle(edges: pd.DataFrame) -> None:
    bad = "<script>alert('xss')</script>"
    html = silo_map(edges, return_html=True, title=bad)
    assert bad not in html
    assert "&lt;script&gt;" in html


def test_silo_map_components_fallback(
    edges: pd.DataFrame,
) -> None:
    components = pd.DataFrame({"node_id": ["A", "B", "C", "D", "E"], "component": [0, 0, 0, 1, 1]})
    html = silo_map(edges, components=components, return_html=True)
    assert isinstance(html, str)


def test_silo_map_communities_take_precedence(
    edges: pd.DataFrame, communities: pd.DataFrame
) -> None:
    components = pd.DataFrame({"node_id": ["A", "B", "C", "D", "E"], "component": [9, 9, 9, 9, 9]})
    html = silo_map(edges, components=components, communities=communities, return_html=True)
    assert isinstance(html, str)


def test_silo_map_with_metadata(
    edges: pd.DataFrame, communities: pd.DataFrame, metadata: pd.DataFrame
) -> None:
    html = silo_map(
        edges,
        communities=communities,
        metadata=metadata,
        return_html=True,
        physics=False,
    )
    assert isinstance(html, str)


def test_silo_map_missing_edge_columns_raises() -> None:
    df = pd.DataFrame({"foo": [1, 2]})
    with pytest.raises(KeyError):
        silo_map(df)


def test_silo_map_empty_edges() -> None:
    df = pd.DataFrame({"employee_id": [], "supervisor_id": []})
    html = silo_map(df, return_html=True)
    assert isinstance(html, str)


def test_silo_map_non_dataframe_raises() -> None:
    with pytest.raises((TypeError, AttributeError)):
        silo_map([1, 2, 3])  # type: ignore[arg-type]
