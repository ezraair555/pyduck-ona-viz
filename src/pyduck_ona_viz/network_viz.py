"""
Network visualizations for ONA outputs.

- :func:`centrality_dashboard` - 2×2 panel comparing the four classical
  centrality measures (betweenness, pagerank, eigenvector, degree).
- :func:`silo_map`             - Community-coloured network map (pyvis
  interactive HTML + matplotlib static fallback).
"""

from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING, Any

import networkx as nx
import numpy as np
import pandas as pd

from pyduck_ona_viz.theme import (
    CATEGORICAL,
    PALETTE,
    apply_default_style,
    category_colors,
    configure_axes,
    new_figure,
)

if TYPE_CHECKING:
    import matplotlib.axes as mpl_axes
    import matplotlib.figure as mpl_figure


# ---------------------------------------------------------------------------
# Centrality dashboard
# ---------------------------------------------------------------------------


def centrality_dashboard(
    betweenness: pd.DataFrame,
    pagerank: pd.DataFrame,
    eigenvector: pd.DataFrame,
    degree: pd.DataFrame,
    *,
    id_col: str = "node_id",
    betweenness_col: str = "betweenness",
    pagerank_col: str = "pagerank",
    eigenvector_col: str = "eigenvector",
    degree_col: str = "degree",
    metadata: pd.DataFrame | None = None,
    name_col: str = "name",
    department_col: str | None = "department",
    top_n: int = 12,
    title: str | None = None,
    figsize: tuple[float, float] = (13.0, 9.0),
) -> mpl_figure.Figure:
    """Plot a 2×2 grid comparing four centrality measures.

    Each panel is a horizontal bar chart of the top ``top_n`` nodes by
    the panel's score. If ``metadata`` and ``department_col`` are supplied,
    bars are coloured by department.

    Parameters
    ----------
    betweenness, pagerank, eigenvector, degree
        DataFrames containing centrality scores per node.
    id_col
        Node identifier column.
    betweenness_col, pagerank_col, eigenvector_col, degree_col
        Score columns in each respective frame.
    metadata
        Optional per-node metadata keyed by ``id_col``.
    name_col
        Display-name column in ``metadata``.
    department_col
        Optional column for department-based bar colours.
    top_n
        Number of top-scoring nodes per panel.
    title
        Optional dashboard title.
    figsize
        Figure size in inches.

    Returns
    -------
    matplotlib.figure.Figure

    Examples
    --------
    >>> import pandas as pd
    >>> import pyduck_ona_viz as viz
    >>> ids = ["A", "B", "C"]
    >>> df = pd.DataFrame({"node_id": ids, "betweenness": [0.5, 0.3, 0.2]})
    >>> others = pd.DataFrame({"node_id": ids, "pagerank": [0.4, 0.3, 0.3]})
    >>> fig = viz.centrality_dashboard(df, others, others.copy(), others.copy(), top_n=3)
    """
    frames: list[tuple[pd.DataFrame, str, str, str]] = [
        (
            betweenness,
            betweenness_col,
            "Betweenness Centrality",
            "Broker nodes — control information flow.",
        ),
        (pagerank, pagerank_col, "PageRank", "Most-influential nodes by random-walk mass."),
        (
            eigenvector,
            eigenvector_col,
            "Eigenvector Centrality",
            "Connected to other well-connected nodes.",
        ),
        (degree, degree_col, "Degree Centrality", "Raw direct connections (in / out degree)."),
    ]

    # Resolve names + departments via vectorized lookups.
    name_lookup: dict[str, str] = {}
    dept_lookup: dict[str, str] = {}
    if metadata is not None and id_col in metadata.columns:
        if name_col in metadata.columns:
            name_lookup = (
                metadata.set_index(id_col)[name_col]
                .apply(lambda v: str(v) if not pd.isna(v) else "")
                .to_dict()
            )
        if department_col and department_col in metadata.columns:
            dept_lookup = (
                metadata.set_index(id_col)[department_col]
                .apply(lambda v: str(v) if not pd.isna(v) else "")
                .to_dict()
            )

    apply_default_style()
    fig, raw_axes = new_figure(figsize=figsize, nrows=2, ncols=2)
    if not isinstance(raw_axes, np.ndarray) or raw_axes.shape != (2, 2):
        raise TypeError("expected a 2×2 ndarray of Axes")
    axes: np.ndarray = raw_axes

    title = title or "Network Centrality Dashboard"
    fig.suptitle(
        title,
        fontsize=18,
        fontweight="semibold",
        color=PALETTE["primary"],
        x=0.06,
        ha="left",
        y=0.99,
    )

    for ax, (df, col, panel_title, subtitle) in zip(axes.flat, frames, strict=False):
        if id_col not in df.columns:
            raise KeyError(f"Column '{id_col}' not in one of the centrality frames")
        if col not in df.columns:
            raise KeyError(f"Column '{col}' not in one of the centrality frames")
        work = df[[id_col, col]].copy()
        work[col] = work[col].fillna(0).astype(float)
        work = work.sort_values(col, ascending=False).head(int(top_n))
        work = work.sort_values(col, ascending=True)

        labels = [name_lookup.get(str(k), str(k)) for k in work[id_col]]
        values = work[col].astype(float).tolist()

        bar_colors: list[str] | str = PALETTE["primary"]
        if dept_lookup:
            depts = [dept_lookup.get(str(k), "Unknown") for k in work[id_col]]
            distinct = sorted(set(depts))
            palette = {d: category_colors(len(distinct))[i] for i, d in enumerate(distinct)}
            bar_colors = [palette[d] for d in depts]

        ax.barh(range(len(labels)), values, color=bar_colors, edgecolor="white", linewidth=0.5)
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels, fontsize=9)
        ax.set_title(
            panel_title,
            loc="left",
            pad=18,
            fontsize=14,
            fontweight="semibold",
            color=PALETTE["primary"],
        )
        ax.text(
            0.0,
            1.02,
            subtitle,
            transform=ax.transAxes,
            fontsize=9.5,
            color=PALETTE["neutral_lt"],
            ha="left",
            va="bottom",
        )
        configure_axes(ax, grid=True, grid_axis="x")
        ax.set_xlabel(col.replace("_", " "), fontsize=10)
        for i, v in enumerate(values):
            ax.text(v, i, f" {v:.3g}", va="center", ha="left", fontsize=8, color=PALETTE["neutral"])

    return fig


# ---------------------------------------------------------------------------
# Silo map (network of communities)
# ---------------------------------------------------------------------------


def silo_map(
    edges: pd.DataFrame,
    components: pd.DataFrame | None = None,
    communities: pd.DataFrame | None = None,
    *,
    source_col: str = "employee_id",
    target_col: str = "supervisor_id",
    node_col: str = "node_id",
    component_col: str = "component",
    community_col: str = "community",
    metadata: pd.DataFrame | None = None,
    name_col: str = "name",
    department_col: str | None = None,
    title: str | None = None,
    figsize: tuple[float, float] = (12.0, 9.0),
    return_html: bool = False,
    physics: bool = True,
) -> mpl_figure.Figure | str:
    """Render an organisational silo map.

    If both ``components`` and ``communities`` are given, ``communities``
    takes precedence (it's the more analytically interesting partition).

    Parameters
    ----------
    edges
        Edge list with ``source_col`` and ``target_col``.
    components, communities
        Optional partition assignments keyed by ``node_col``.
    source_col
        Source node column in ``edges``.
    target_col
        Target node column in ``edges``.
    node_col
        Node identifier column in partition and metadata frames.
    component_col
        Column in ``components``.
    community_col
        Column in ``communities``.
    metadata
        Optional per-node metadata keyed by ``node_col``.
    name_col
        Display-name column in ``metadata``.
    department_col
        Optional department column in ``metadata``.
    title
        Optional chart title.
    figsize
        Figure size in inches.
    return_html
        If True, return pyvis interactive HTML; otherwise a matplotlib Figure.
    physics
        If True, enable pyvis physics simulation.

    Returns
    -------
    matplotlib.figure.Figure or str

    Examples
    --------
    >>> import pandas as pd
    >>> import pyduck_ona_viz as viz
    >>> edges = pd.DataFrame({
    ...     "employee_id": ["A", "B"],
    ...     "supervisor_id": ["B", "C"],
    ... })
    >>> fig = viz.silo_map(edges)
    """
    if source_col not in edges.columns or target_col not in edges.columns:
        raise KeyError(f"Edge DataFrame must contain '{source_col}' and '{target_col}'")

    graph: nx.DiGraph[str] = nx.DiGraph()
    # Vectorized edge construction.
    edge_pairs = (
        edges[[source_col, target_col]]
        .dropna(subset=[source_col, target_col])
        .assign(u=lambda f: f[source_col].astype(str), v=lambda f: f[target_col].astype(str))[
            ["u", "v"]
        ]
        .to_records(index=False)
        .tolist()
    )
    graph.add_edges_from(edge_pairs)

    partition_source = communities if communities is not None else components
    partition_col = community_col if communities is not None else component_col

    if partition_source is None or partition_col not in partition_source.columns:
        node_partition: dict[str, int] = {n: i for i, n in enumerate(graph.nodes())}
    else:
        node_partition = {
            str(row[node_col]): int(row[partition_col])
            for row in partition_source[[node_col, partition_col]]
            .dropna(subset=[partition_col])
            .to_dict("records")
        }

    # Metadata: name + department via vectorized lookup.
    name_lookup: dict[str, str] = {}
    dept_lookup: dict[str, str] = {}
    if metadata is not None and node_col in metadata.columns:
        if name_col in metadata.columns:
            name_lookup = (
                metadata.set_index(node_col)[name_col]
                .apply(lambda v: str(v) if not pd.isna(v) else "")
                .to_dict()
            )
        if department_col and department_col in metadata.columns:
            dept_lookup = (
                metadata.set_index(node_col)[department_col]
                .apply(lambda v: str(v) if not pd.isna(v) else "")
                .to_dict()
            )

    # Stable colour map per partition id
    pids = sorted(set(node_partition.values()))
    palette = {pid: CATEGORICAL[i % len(CATEGORICAL)] for i, pid in enumerate(pids)}

    title = title or "Organizational Silo Map"
    subtitle = (
        f"Coloured by Louvain communities · {len(pids)} silos"
        if communities is not None
        else f"Coloured by connected components · {len(pids)} components"
    )

    if return_html:
        return _silo_map_pyvis(
            graph,
            node_partition,
            palette,
            name_lookup,
            dept_lookup,
            title=title,
            subtitle=subtitle,
            physics=physics,
        )
    return _silo_map_matplotlib(
        graph,
        node_partition,
        palette,
        name_lookup,
        dept_lookup,
        title=title,
        subtitle=subtitle,
        figsize=figsize,
    )


def _silo_map_matplotlib(
    graph: nx.DiGraph[str],
    node_partition: dict[str, int],
    palette: dict[int, str],
    name_lookup: dict[str, str],
    dept_lookup: dict[str, str],
    *,
    title: str,
    subtitle: str,
    figsize: tuple[float, float],
) -> mpl_figure.Figure:
    """Render a static matplotlib silo map.

    Parameters
    ----------
    graph
        Directed graph of organisation edges.
    node_partition
        Mapping from node ID to partition ID.
    palette
        Mapping from partition ID to colour.
    name_lookup, dept_lookup
        Optional display names / departments per node.
    title
        Chart title.
    subtitle
        Chart subtitle.
    figsize
        Figure size in inches.

    Returns
    -------
    matplotlib.figure.Figure
    """
    import matplotlib.patches as mpatches

    apply_default_style()
    fig, raw_ax = new_figure(figsize=figsize)
    ax = _cast_single_axes(raw_ax)

    # Use an undirected view for the layout to avoid arrowhead clutter.
    undirected = graph.to_undirected()
    pos = nx.spring_layout(
        undirected,
        seed=42,
        k=1.0 / max(len(undirected), 1) ** 0.5,
    )

    # Node sizes proportional to degree
    deg = dict(graph.degree())
    nodes = list(undirected.nodes())
    sizes = [30 + 18 * deg.get(n, 0) for n in nodes]
    colors = [palette[node_partition.get(n, 0)] for n in nodes]

    nx.draw_networkx_edges(
        undirected,
        pos,
        ax=ax,
        alpha=0.25,
        edge_color=PALETTE["neutral_lt"],
        width=0.7,
    )
    nx.draw_networkx_nodes(
        undirected,
        pos,
        ax=ax,
        node_size=sizes,
        node_color=colors,
        edgecolors="white",
        linewidths=1.0,
        alpha=0.9,
    )

    # Label only the largest nodes by degree (top 10)
    top = sorted(deg.items(), key=lambda kv: -kv[1])[:10]
    label_pos = {n: pos[n] for n, _ in top}
    labels = {n: name_lookup.get(n, n) for n, _ in top}
    nx.draw_networkx_labels(
        undirected,
        label_pos,
        labels=labels,
        ax=ax,
        font_size=8.5,
        font_color=PALETTE["primary"],
        font_weight="bold",
    )

    ax.set_title(
        title,
        loc="left",
        pad=28,
        fontsize=16,
        fontweight="semibold",
        color=PALETTE["primary"],
    )
    ax.text(
        0.0,
        1.02,
        subtitle,
        transform=ax.transAxes,
        fontsize=10,
        color=PALETTE["neutral_lt"],
        ha="left",
        va="bottom",
    )
    ax.set_axis_off()

    # Legend
    handles = [
        mpatches.Patch(color=palette[pid], label=str(pid)) for pid in sorted(palette.keys())[:12]
    ]
    ax.legend(
        handles=handles,
        loc="lower left",
        title=subtitle.split("·")[0].strip(),
        fontsize=8.5,
        title_fontsize=9,
        frameon=True,
        facecolor="white",
        edgecolor="#E5E5E5",
    )

    return fig


def _silo_map_pyvis(
    graph: nx.DiGraph[str],
    node_partition: dict[str, int],
    palette: dict[int, str],
    name_lookup: dict[str, str],
    dept_lookup: dict[str, str],
    *,
    title: str,
    subtitle: str,
    physics: bool,
) -> str:
    """Render an interactive PyVis HTML silo map.

    Parameters
    ----------
    graph
        Directed graph of organisation edges.
    node_partition
        Mapping from node ID to partition ID.
    palette
        Mapping from partition ID to colour.
    name_lookup, dept_lookup
        Optional display names / departments per node.
    title
        Page title and heading.
    subtitle
        Subtitle shown under the heading.
    physics
        Whether to enable physics simulation.

    Returns
    -------
    str
        Standalone HTML document with an embedded PyVis network.
    """
    from pyvis.network import Network

    safe_title = escape(title)
    safe_subtitle = escape(subtitle)

    net = Network(
        height="780px",
        width="100%",
        directed=True,
        notebook=False,
        cdn_resources="remote",
        heading=safe_title,
        bgcolor="white",
        font_color=PALETTE["neutral"],
    )
    if not physics:
        net.toggle_physics(False)

    deg = dict(graph.degree())
    for n in graph.nodes():
        label = escape(name_lookup.get(n, str(n)))
        title_attr = escape(
            "\n".join(
                filter(
                    None,
                    [
                        name_lookup.get(n, str(n)),
                        dept_lookup.get(n, ""),
                        f"degree = {deg.get(n, 0)}",
                        f"silo = {node_partition.get(n, '?')}",
                    ],
                )
            )
        )
        net.add_node(
            str(n),
            label=label,
            title=title_attr,
            color=palette[node_partition.get(n, 0)],
            size=18 + 4 * deg.get(n, 0),
        )
    for u, v in graph.edges():
        net.add_edge(str(u), str(v), color="#BFBFBF", arrows="to")

    html = net.generate_html(notebook=False)
    # Wrap in a proper HTML doc with the escaped subtitle
    wrapped = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>{safe_title}</title>
<style>
  body {{ margin: 0; font-family: 'DejaVu Sans', sans-serif; background: {PALETTE["background"]}; color: {PALETTE["neutral"]}; }}
  #header {{ padding: 16px 24px; background: white; border-bottom: 1px solid #E5E5E5; }}
  #header h1 {{ margin: 0; font-size: 18px; font-weight: 600; color: {PALETTE["primary"]}; }}
  #header .sub {{ font-size: 12px; color: {PALETTE["neutral_lt"]}; margin-top: 2px; }}
</style>
</head><body>
<div id="header">
  <h1>{safe_title}</h1>
  <div class="sub">{safe_subtitle}</div>
</div>
{html}
</body></html>"""
    return wrapped


def _cast_single_axes(ax: Any) -> mpl_axes.Axes:
    """Cast a single subplot axes to ``mpl_axes.Axes``.

    Parameters
    ----------
    ax
        Axes returned by ``new_figure``.

    Returns
    -------
    matplotlib.axes.Axes
        A single Axes object.

    Raises
    ------
    TypeError
        If ``ax`` is not a single Axes.
    """
    from matplotlib.axes import Axes

    if isinstance(ax, Axes):
        return ax
    raise TypeError("expected a single Axes instance")


__all__ = ["centrality_dashboard", "silo_map"]
