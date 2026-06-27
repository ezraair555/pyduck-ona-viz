# pyduck-ona-viz

> Publication-quality visualizations for organizational chart analysis
> and people analytics. Companion package to
> [`pyduck-ona`](https://github.com/ezraair555/pyduck-ona).

`pyduck-ona-viz` takes the DuckDB-relation outputs of `pyduck-ona`
(hierarchy stats, centrality frames, communities, attrition tables…)
and turns them into polished, presentation-ready figures.

- **Static matplotlib figures** for embedding into reports and slide decks.
- **Interactive HTML** (D3 + Plotly + pyvis) for exploratory dashboards.

The design language is consistent across every function: a deep-blue /
warm-gray / coral palette, no chartjunk, 11 pt axis labels, 16 pt titles,
150 DPI for screen / 300 DPI for print.

---

## Installation

```bash
pip install pyduck-ona-viz

# For the interactive dashboards (Plotly HTML, pyvis silo maps):
pip install "pyduck-ona-viz[interactive]"

# To also pull in pyduck-ona itself:
pip install "pyduck-ona-viz[full]"
```

Or, from this repo:

```bash
pip install -e .
pip install -e ".[interactive]"
```

---

## Quick start

```python
import pyduck_ona as pona
import pyduck_ona_viz as viz

# pyduck-ona produces DuckDB relations; .df() gives us pandas DataFrames.
long_df  = pona.hierarchy_long(rel, "employee_id", "supervisor_id").df()
stats_df = pona.hierarchy_stats(rel, "employee_id", "supervisor_id").df()

# 1. Span-of-control bar chart
fig = viz.span_of_control(stats_df, top_n=20)

# 2. Interactive org chart (HTML string)
html = viz.org_chart_tree(long_df, metadata=employees_df)

# 3. Single-page executive dashboard
html = viz.summary_dashboard(stats_df, betweenness=b.df(), pagerank=pr.df())
```

---

## Functions

| Function | Output | Use case |
|---|---|---|
| `org_chart_tree` | Interactive HTML (D3) | Executive org chart with collapsible nodes. |
| `reporting_chain_walk` | matplotlib Figure | Clean path from any employee up to the top. |
| `span_of_control` | Figure or Plotly HTML | Top managers by direct reports. |
| `span_vs_depth` | Figure | Quadrant bubble chart (efficient / top-heavy / flat / deep). |
| `hierarchy_depth_heatmap` | Figure | Matrix of employees × levels. |
| `centrality_dashboard` | Figure (2×2) | Compare betweenness / PageRank / eigenvector / degree. |
| `silo_map` | HTML or Figure | Community-coloured network map. |
| `attrition_heatmap` | Figure | Department × level attrition rates. |
| `compensation_equity` | Figure | Tenure / level vs salary, with regression + outliers. |
| `summary_dashboard` | HTML | One-page executive dashboard. |

---

## Examples

### Interactive org chart

```python
import pyduck_ona as pona
import pyduck_ona_viz as viz

long_df = pona.hierarchy_long(rel, "employee_id", "supervisor_id").df()
metadata = employees_df  # must contain employee_id + name + title + department

html = viz.org_chart_tree(
    long_df,
    metadata=metadata,
    color_by="department",
    title="Acme Corp · Q4 2026",
)
Path("org.html").write_text(html)
```

> _Screenshot placeholder_: A horizontal D3 tree with nodes coloured by
> department, a legend in the top-right, and zoom/expand controls in the
> bottom-right.

### Span of control

```python
fig = viz.span_of_control(
    stats_df,
    metadata=employees_df,
    top_n=15,
    color_by_department=True,
)
fig.savefig("span.png", dpi=300, bbox_inches="tight")
```

> _Screenshot placeholder_: A horizontal bar chart with the largest team at
> the top, annotated counts at the bar tips, a dashed median reference line,
> and bars coloured by department.

### Centrality dashboard

```python
fig = viz.centrality_dashboard(
    betweenness=b.df(),
    pagerank=pr.df(),
    eigenvector=ev.df(),
    degree=dg.df(),
    metadata=employees_df,
    top_n=10,
)
```

> _Screenshot placeholder_: A 2×2 grid of bar charts, each with subtitle
> and top-10 colouring by department.

### Silo map

```python
# Interactive HTML
html = viz.silo_map(edges_df, communities=comms.df(), return_html=True)

# Static fallback for a slide deck
fig = viz.silo_map(edges_df, communities=comms.df(), return_html=False)
```

> _Screenshot placeholder_: A force-directed network with each community
> coloured differently, only the highest-degree nodes labelled.

### Compensation equity

```python
fig = viz.compensation_equity(
    comp_df,
    x_col="tenure_years",
    y_col="salary",
    group_col="gender",
)
```

> _Screenshot placeholder_: Scatter coloured by group with two regression
> lines and an overall fit. Outliers (1.5×IQR from the overall line) are
> circled in red with names annotated. A small badge in the corner shows
> the median salary gap between the two groups.

### Summary dashboard

```python
html = viz.summary_dashboard(
    hierarchy_stats=stats_df,
    betweenness=b.df(),
    pagerank=pr.df(),
    diversity=diversity_df,
    attrition=attrition_df,
)
Path("dashboard.html").write_text(html)
```

> _Screenshot placeholder_: A single page with KPI cards across the top
> (headcount, managers, avg span, max depth) and a 2-column grid of
> interactive Plotly panels below: span bars, span histogram, top brokers,
> top PageRank, diversity mix, attrition heatmap.

---

## Design language

All functions share a single visual identity defined in
`pyduck_ona_viz.theme`:

- **Palette**: deep blue (`#1F3A5F`), coral accent (`#E27D60`), warm gray
  text (`#4D4D4D`), sage success (`#5B9279`), brick danger (`#C44536`).
- **Typography**: DejaVu Sans throughout. Titles 16 pt semibold, axes 11 pt,
  ticks 10 pt, annotations 9 pt.
- **Layout**: `constrained_layout=True` everywhere; no top/right spines
  on bar charts; only horizontal grid on bar charts.
- **DPI**: 150 default; pass `dpi=300` to `savefig` for print.
- **Categorical colour cycling**: deterministic from
  `pyduck_ona_viz.CATEGORICAL`.

If you need a different brand palette, copy `theme.py` and override
`PALETTE` / `CATEGORICAL` — every function reads from there.

---

## API patterns

Every visualization function:

1. **Accepts a DataFrame** (the `.df()` of a pyduck-ona relation) plus
   optional `metadata=` DataFrame keyed by employee id.
2. **Returns either** a `matplotlib.figure.Figure` or a `str` of HTML.
   Nothing is ever rendered to screen — `plt.show()` is never called.
3. **Validates input** column names and raises `KeyError` / `TypeError`
   with clear messages.

Interactive variants are exposed via `return_html=True` on the functions
that support them (`span_of_control`, `silo_map`).

---

## Running the demo

```bash
git clone https://github.com/ezraair555/pyduck-ona-viz
cd pyduck-ona-viz
pip install -e ".[interactive,full]"
python examples/full_viz_demo.py
```

The demo builds a synthetic 300-person org with realistic hierarchy stats,
runs every visualization, and writes them to `examples/output/`.

---

## Testing

```bash
pytest tests/
```

Smoke tests verify that every function returns the correct type
(Figure or HTML str) when fed synthetic data.

---

## License

MIT © 2026 EzraAir555. See [LICENSE](LICENSE).