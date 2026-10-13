# AGENTS.md

Guidance for automated agents working on `china-ratlas`.

## Project Overview

- R (v4.6) + Python + Quarto geospatial pipeline producing a static exploratory spatial atlas of 47 Chinese cities.
- Deployed via GitHub Pages from the `docs/` directory (`output-dir: docs`).

## Core Commands

- **Full rebuild pipeline**: `Rscript run_atlas.R`
- **Render website only**: `quarto render`
- **Render a single page**: `quarto render index.qmd` or `quarto render cities/chengdu.qmd`
- **Local preview**: `quarto preview`
- **Verify no escaped code blocks in HTML**:
  ```bash
  python3 -c "import glob, re; errs = [p for p in glob.glob('docs/**/*.html', recursive=True) if '<pre><code>' in open(p).read()]; print('Unintended code blocks:', len(errs)); assert not errs"
  ```

## Pipeline Execution Order

When updating data, calculations, or page layouts, execute in this order:

1. `python3 scripts/create_city_registry.py`, `python3 scripts/build_china_hsr.py`, `python3 scripts/extract_city_railways.py`, & `python3 scripts/fetch_city_wiki_resources.py` (updates master metadata, HSR vectors, city rail layers, and Wikipedia/Wikimedia resources)
2. `Rscript R/02_fetch_and_crop_wsf.R` (fetches/crops DLR WSF 30m rasters; skips cached `.tif`)
3. `Rscript R/03_compute_growth_metrics.R` (recalculates area km², 2020 census population ranks, and multipliers)
4. `Rscript R/04_generate_atlas_maps.R` (batch renders PNG maps and charts; parallelized on 4 cores)
5. `python3 scripts/generate_quarto_pages.py` (generates all `.qmd` files in `cities/` and `regions/`)
6. `quarto render` (compiles to `docs/`)

## Critical Toolchain & Environment Quirks

- **R Package Installation**: `bspm` is enabled in this environment. If installing user packages without sudo/dbus errors, disable `bspm` first:
  ```R
  bspm::disable(); install.packages("pkgname", repos="https://cloud.r-project.org")
  ```
- **Quarto Raw HTML Gotcha**: NEVER indent raw HTML blocks with 4 spaces in Markdown or within Pandoc divs (`::: {.hero-banner}`); Pandoc treats 4-space indents as code blocks (`<pre><code>`), leaking raw HTML markup to the rendered page. Always enclose custom HTML blocks (banners, clickable image maps, navigation bars) inside explicit ````{=html} ... ```` fences.
- **CJK Font for ggplot2**: Chinese characters require the system font `Droid Sans Fallback` with `ragg::agg_png`. In ggplot2 themes, set `base_family = "Droid Sans Fallback"`.
- **Terra Raster Merging**: When merging multiple SpatRaster tiles in `terra`, pass a `sprc` collection: `merge(sprc(rasters))` instead of calling `merge()` directly on a list.
- **Remote Raster Access**: DLR WSF Evolution tiles stream over HTTP range requests via `/vsicurl/https://download.geoservice.dlr.de/WSF_EVO/files/...`. Always crop to city bounding box and write compressed GeoTIFFs (`COMPRESS=DEFLATE`).
- **GitHub Pages Requirement**: The compiled output lives in `docs/`. Both `docs/.nojekyll` and root `.nojekyll` must remain present so GitHub Pages does not ignore underscore directories like `site_libs`.
- **Large Data Gitignore**: `data/raw/*.geojson` and `data/raw/hotosm_railways/` are gitignored due to size (>300 MB). Store only aggregated geometries in `data/processed/*.rds` or `*.geojson`.
