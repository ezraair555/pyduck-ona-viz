# Changelog

All notable changes to `pyduck-ona-viz` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-06-27

### Added
- GitHub Actions CI matrix on Python 3.10, 3.11, 3.12 running lint, format,
  type-check, and pytest with 90% coverage enforcement.
- `.gitignore`, `.pre-commit-config.yaml`, `MANIFEST.in`, `CHANGELOG.md`,
  `SECURITY.md`, `CODE_OF_CONDUCT.md`, and `CONTRIBUTING.md`.
- MkDocs site under `docs/` with the Material theme and `mkdocstrings` API
  reference.
- Comprehensive test suite split by module with edge-case, error-path, XSS, and
  performance tests (100+ tests, ≥90% line coverage).
- Parametrized examples with deterministic seeding; Jupyter demo notebook and
  `examples/gallery.md`.

### Fixed
- **Security**: escaped all user-supplied strings before interpolating them into
  HTML/JS in `org_chart.py`, `network_viz.py`, `dashboard.py`, and
  `span_control.py`.
- **Type safety**: full `mypy` annotations on internal helpers; corrected
  `gradient_color` / `gradient_color_palette` return types to RGBA tuples;
  fixed `bar_colors` union and `hr_viz` assignment.
- **Error handling**: `org_chart_tree` now validates `root_id` exists in the
  children map; `reporting_chain_walk` raises on cycles; `_normalize_hierarchy`
  rejects duplicate employee IDs.
- **Performance**: replaced `iterrows()` loops with vectorized/groupby
  equivalents in `span_control.py`, `network_viz.py`, and `org_chart.py`.

### Changed
- `id_col` now defaults to `"employee_id"` consistently across all
  hierarchy-aware functions. `span_of_control` still accepts a different
  column (e.g., `"manager_id"`) when explicitly provided.

### Removed
- Dead `_CENTRALITY_PANELS` constant in `network_viz.py`.
- Unused `label_col` parameter from `_prepare_stats` in `span_control.py`.
- Dead pivot block in `tests/test_viz.py`.

## [0.1.0] - 2026-06-20

### Added
- Initial release of `pyduck-ona-viz` with ten visualization entry points:
  `org_chart_tree`, `reporting_chain_walk`, `span_of_control`, `span_vs_depth`,
  `hierarchy_depth_heatmap`, `centrality_dashboard`, `silo_map`,
  `attrition_heatmap`, `compensation_equity`, and `summary_dashboard`.
- Shared brand palette, typography, and figure helpers in `theme.py`.
- Optional interactive backends via Plotly and pyvis.
- Synthetic end-to-end demo in `examples/full_viz_demo.py`.
