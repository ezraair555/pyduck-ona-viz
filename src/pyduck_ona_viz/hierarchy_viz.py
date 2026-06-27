"""
Hierarchy depth visualizations.

- :func:`hierarchy_depth_heatmap` - Matrix view: rows = employees, columns
  = levels, showing who reports to whom at each depth. Useful for spotting
  flat vs deep org structures.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

from pyduck_ona_viz.theme import (
    BLUES_CMAP,
    PALETTE,
    apply_default_style,
    configure_axes,
    new_figure,
    style_axis_labels,
)

if TYPE_CHECKING:
    import matplotlib.axes as mpl_axes
    import matplotlib.figure as mpl_figure


def hierarchy_depth_heatmap(
    df: pd.DataFrame,
    *,
    employee_col: str = "employee_id",
    level_prefix: str = "Level_",
    max_levels: int | None = None,
    metadata: pd.DataFrame | None = None,
    name_col: str = "name",
    title: str | None = None,
    figsize: tuple[float, float] = (10.0, 9.0),
    annotate: bool = False,
) -> mpl_figure.Figure:
    """Render the hierarchy-wide table as a heatmap of depth vs employee.

    Parameters
    ----------
    df
        Wide-form hierarchy (output of ``pyduck_ona.hierarchy_wide(...)``).
        Columns ``Level_1``, ``Level_2``, ... are depth columns; each cell
        contains the manager_id at that depth (or NaN).
    employee_col
        Column holding the employee identifier.
    level_prefix
        Prefix for level columns. Defaults to ``"Level_"``.
    max_levels
        Optional cap on the number of levels rendered.
    metadata
        Optional per-employee metadata, used to label rows with names.
    name_col
        Column in ``metadata`` holding display names.
    title
        Optional chart title.
    figsize
        Figure size in inches.
    annotate
        Whether to write manager IDs inside occupied cells.

    Returns
    -------
    matplotlib.figure.Figure

    Examples
    --------
    >>> import pandas as pd
    >>> import pyduck_ona_viz as viz
    >>> df = pd.DataFrame({
    ...     "employee_id": ["E1", "E2", "E3"],
    ...     "Level_1": ["CEO", "CEO", "M1"],
    ...     "Level_2": [np.nan, np.nan, "CEO"],
    ... })
    >>> fig = viz.hierarchy_depth_heatmap(df)
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("`df` must be a pandas DataFrame")
    if employee_col not in df.columns:
        raise KeyError(f"Column '{employee_col}' not found in DataFrame")

    level_cols = [c for c in df.columns if c.startswith(level_prefix)]
    if not level_cols:
        raise ValueError(
            f"No columns starting with '{level_prefix}' found. "
            "Pass the output of pyduck_ona.hierarchy_wide(...)."
        )
    level_cols = sorted(level_cols, key=lambda c: int(c[len(level_prefix) :]))
    if max_levels is not None:
        level_cols = level_cols[: int(max_levels)]

    # Build numeric matrix: 1 where employee has a manager at that depth, 0 otherwise.
    matrix = df[level_cols].notna().astype(int).to_numpy()

    name_lookup: dict[str, str] = {}
    if metadata is not None and employee_col in metadata.columns and name_col in metadata.columns:
        name_lookup = (
            metadata.set_index(employee_col)[name_col]
            .apply(lambda v: str(v) if not pd.isna(v) else "")
            .to_dict()
        )

    if name_lookup:
        row_labels = [name_lookup.get(str(eid), str(eid)) for eid in df[employee_col]]
    else:
        row_labels = df[employee_col].astype(str).tolist()

    # Sort employees by the deepest level they reach (deepest at top)
    deepest = (matrix * np.arange(1, matrix.shape[1] + 1)).max(axis=1)
    order = np.argsort(-deepest, kind="stable")
    matrix = matrix[order]
    row_labels = [row_labels[i] for i in order]

    apply_default_style()
    fig, raw_ax = new_figure(figsize=figsize)
    ax = _cast_single_axes(raw_ax)
    im = ax.imshow(
        matrix,
        aspect="auto",
        cmap=BLUES_CMAP,
        interpolation="nearest",
        vmin=0,
        vmax=1,
    )

    ax.set_xticks(np.arange(len(level_cols)))
    ax.set_xticklabels([c.replace(level_prefix, "L") for c in level_cols])
    ax.set_yticks(np.arange(len(row_labels)))
    ax.set_yticklabels(row_labels, fontsize=8)

    # Move x labels to the top
    ax.xaxis.tick_top()
    ax.tick_params(top=False, left=False)

    # Annotate cells with the manager id (if known) for richness
    if annotate:
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                if matrix[i, j]:
                    val = df.iloc[order[i]][level_cols[j]]
                    if pd.notna(val):
                        manager = name_lookup.get(str(val), str(val))
                        short = manager if len(manager) <= 14 else manager[:13] + "…"
                        ax.text(
                            j,
                            i,
                            short,
                            ha="center",
                            va="center",
                            fontsize=7,
                            color="white" if j < 2 else PALETTE["neutral"],
                        )

    title = title or "Hierarchy Depth Heatmap"
    style_axis_labels(
        ax,
        xlabel="",
        ylabel="",
        title=title,
        subtitle="Each cell = employee has an ancestor at that depth",
    )

    cbar = fig.colorbar(im, ax=ax, shrink=0.4, pad=0.02)
    cbar.set_ticks([0, 1])
    cbar.set_ticklabels(["no link", "manages"])
    cbar.outline.set_visible(False)  # type: ignore[operator]

    configure_axes(ax, grid=False)
    # Add a thin separator between cells
    ax.set_xticks(np.arange(matrix.shape[1] + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(matrix.shape[0] + 1) - 0.5, minor=True)
    ax.grid(which="minor", color="white", linewidth=1.2)
    ax.tick_params(which="minor", length=0)

    return fig


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


__all__ = ["hierarchy_depth_heatmap"]
