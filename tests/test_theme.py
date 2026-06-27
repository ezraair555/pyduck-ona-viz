"""Tests for ``pyduck_ona_viz.theme``."""

from __future__ import annotations

import matplotlib
import matplotlib.figure as mfigure
import numpy as np
import pytest

matplotlib.use("Agg")

from pyduck_ona_viz.theme import (
    CATEGORICAL,
    PALETTE,
    apply_default_style,
    category_colors,
    color_for,
    configure_axes,
    gradient_color,
    gradient_color_palette,
    new_figure,
    style_axis_labels,
)


@pytest.mark.parametrize("color_name", list(PALETTE.keys()))
def test_palette_values_are_valid_hex(color_name: str) -> None:
    """Every named palette colour is a valid 7-character hex string."""
    value = PALETTE[color_name]
    assert value.startswith("#"), f"{color_name} is not a hex string"
    assert len(value) == 7, f"{color_name} hex length must be 7"
    int(value[1:], 16)  # valid hex digits


def test_category_colors_cycles_correctly() -> None:
    """``category_colors`` returns ``n`` colours, cycling the palette."""
    n = 25
    colors = category_colors(n)
    assert len(colors) == n
    assert colors[: len(CATEGORICAL)] == CATEGORICAL
    assert colors[len(CATEGORICAL)] == CATEGORICAL[0]


@pytest.mark.parametrize("n", [0, -3])
def test_category_colors_non_positive_returns_empty(n: int) -> None:
    assert category_colors(n) == []


def test_color_for_uses_lookup() -> None:
    assert color_for("foo", {"foo": "#123456"}) == "#123456"


def test_color_for_falls_back_to_categorical() -> None:
    value = color_for("some department")
    assert value.startswith("#")
    assert value in CATEGORICAL


def test_apply_default_style_updates_rcparams() -> None:
    import matplotlib as mpl

    apply_default_style()
    assert mpl.rcParams["font.family"][0] == "DejaVu Sans"
    assert mpl.rcParams["axes.spines.top"] is False


def test_new_figure_returns_figure_and_single_axes() -> None:
    fig, ax = new_figure()
    assert isinstance(fig, mfigure.Figure)
    assert len(fig.axes) == 1


def test_new_figure_multi_axes() -> None:
    fig, axes = new_figure(nrows=2, ncols=2)
    assert isinstance(fig, mfigure.Figure)
    assert axes.shape == (2, 2)


def test_configure_axes_applies_grid() -> None:
    fig, ax = new_figure()
    configure_axes(ax, grid=True, grid_axis="both")
    assert ax.xaxis.get_gridlines()[0].get_visible()
    assert ax.yaxis.get_gridlines()[0].get_visible()


@pytest.mark.parametrize(
    ("values", "cmap"),
    [
        ([0.0, 0.5, 1.0], "viridis"),
        (np.array([1.0, 2.0, 3.0]), "plasma"),
        ([], "viridis"),
    ],
)
def test_gradient_color_returns_rgba_tuples(values, cmap) -> None:
    colors = gradient_color(values, cmap=cmap)
    if len(values) == 0:
        assert colors == []
    else:
        assert len(colors) == len(values)
        assert all(isinstance(c, tuple) and len(c) == 4 for c in colors)
        assert all(0.0 <= channel <= 1.0 for c in colors for channel in c)


@pytest.mark.parametrize(
    ("values", "cmap_name"),
    [
        ([0.0, 0.5, 1.0], None),
        ([10.0, 20.0, 30.0], "viridis"),
        ([], None),
    ],
)
def test_gradient_color_palette_returns_rgba_tuples(values, cmap_name) -> None:
    colors = gradient_color_palette(values, cmap_name=cmap_name)
    if len(values) == 0:
        assert colors == []
    else:
        assert len(colors) == len(values)
        assert all(isinstance(c, tuple) and len(c) == 4 for c in colors)


def test_gradient_color_handles_constant_values() -> None:
    colors = gradient_color([5.0, 5.0, 5.0])
    assert len(colors) == 3
    assert all(c == colors[0] for c in colors)


def test_style_axis_labels_sets_text() -> None:
    fig, ax = new_figure()
    style_axis_labels(ax, xlabel="X", ylabel="Y", title="Title", subtitle="Sub")
    assert ax.get_xlabel() == "X"
    assert ax.get_ylabel() == "Y"
    assert ax.get_title(loc="left") == "Title"


def test_module_all_exports_match() -> None:
    from pyduck_ona_viz import theme

    assert set(theme.__all__) <= set(dir(theme))
