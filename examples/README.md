# Examples — pyduck-ona-viz

This directory contains end-to-end usage examples for the package.

## Files

| File | Description |
|---|---|
| `full_viz_demo.py` | Builds a 300-person synthetic organization and renders every visualization in the package. Writes 12 artifacts (8 PNGs + 4 HTMLs) to `output/`. |
| `jupyter_demo.ipynb` | Walk-through of 4 visualizations with markdown explanations. Executes end-to-end with `jupyter nbconvert --execute`. |
| `gallery.md` | Thumbnail gallery linking to each rendered artifact. |
| `output/` | Rendered artifacts. Tracked in git for the README gallery. |

## Reproducibility

`full_viz_demo.py` is **seed-deterministic** at the data level. Every random source uses a single `np.random.default_rng(42)` instance threaded through the build pipeline:

- Hierarchy topology (parent assignment, metadata fields).
- Centrality computation (NetworkX seeded with `seed=42` for Louvain communities).
- Attrition rates (deterministic from seeded RNG).
- DataFrame row ordering is pinned by `(score, node_id)` for centrality frames so near-tied scores don't shuffle.

### Pixel-level determinism

For **11 of 12** rendered artifacts, running the demo twice produces **bit-identical files** (md5 match).

For `04_centrality_dashboard.png`, byte-level md5 may drift between runs by a few bytes while the image is **visually identical** (mean pixel difference < 0.1 / 255 ≈ 0.04%). The drift comes from matplotlib's Agg rasterizer, which has sub-pixel jitter on bar edges even with pinned inputs. This is a known matplotlib limitation, not a data or seed problem.

If you require byte-identical PNGs (e.g., for image diffing in CI), set `matplotlib.rcParams['svg.hashsalt']` and consider exporting to SVG instead.

## Running

```bash
# From repo root:
python examples/full_viz_demo.py
ls examples/output/
```

## Regenerating after a code change

After modifying `src/pyduck_ona_viz/`, run the demo to refresh the gallery:

```bash
python examples/full_viz_demo.py
git add examples/output/
git commit -m "docs(examples): refresh gallery"
```
