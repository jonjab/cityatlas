# AGENTS.md

Guidance for automated agents working on `china-ratlas`.

## Project Overview

- R (v4.6) + Python + Quarto geospatial pipeline producing an exploratory spatial atlas of 47 Chinese cities and 3 US benchmark metropolises (Chicago, Milwaukee, Charlotte).
- Editorial design: *McSweeney's* literary journal typography (warm ivory `#fbf9f4`, rules, serif, sentence case, no forced allcaps) with a map-forward layout.
- Integrated resources: DLR WSF Evolution 30m satellite rasters, China Railway 12306, AMap subways, AGSL Google Drive archival map scans, and the UCSB Esri ArcGIS Web Map (`636bb82ea14944a5b719fc46cf055a53`).
- Static site compiles to `docs/` for GitHub Pages deployment.

## Core Commands

- **Full rebuild pipeline**: `Rscript run_atlas.R`
- **Render website only**: `quarto render`
- **Render single page**: `quarto render index.qmd` or `quarto render cities/chengdu.qmd`
- **Local preview**: `quarto preview`
- **Regenerate pages only (no map re-rendering)**: `python3 scripts/generate_quarto_pages.py && quarto render`
- **Verify no escaped code blocks in HTML**:
  ```bash
  python3 -c "import glob, re; errs = [p for p in glob.glob('docs/**/*.html', recursive=True) if '<pre><code>' in open(p).read()]; print('Unintended code blocks:', len(errs)); assert not errs"
  ```

## Pipeline Execution Order

When updating data, calculations, map aesthetics, or page templates, execute in this order:

1. `python3 scripts/create_city_registry.py`, `python3 scripts/create_comparison_cities.py`, `python3 scripts/build_china_hsr.py`, `python3 scripts/fetch_chinese_transit_datasets.py`, `Rscript scripts/process_chinese_rail_subway.R`, `Rscript scripts/extract_comparison_railways.R`, & `python3 scripts/fetch_city_wiki_resources.py`
2. `Rscript R/02_fetch_and_crop_wsf.R` (fetches/crops DLR WSF 30m rasters; skips cached `.tif`)
3. `Rscript R/03_compute_growth_metrics.R` (recalculates area km², 2020 census population ranks, and multipliers)
4. `Rscript R/04_generate_atlas_maps.R` & `Rscript scripts/generate_comparison_maps.R` (batch renders PNG maps & charts; parallelized on 4 cores)
5. `python3 scripts/generate_quarto_pages.py` (generates all `.qmd` files in `cities/` and `regions/`, as well as `index.qmd`, `comparison.qmd`, and `cities.qmd`)
6. `quarto render` (compiles to `docs/`)

## Critical Toolchain & Codebase Quirks

- **Quarto Raw HTML Gotcha**: NEVER indent raw HTML blocks with 4 spaces in Markdown or within Pandoc divs (`::: {.hero-banner}`); Pandoc treats 4-space indents as code blocks (`<pre><code>`), leaking raw HTML markup to the rendered page. Always enclose custom HTML blocks (banners, clickable image maps, AGSL scan cards, embedded iframes) inside explicit ````{=html} ... ```` fences.
- **Quarto Callouts & Divs**: Use single curly braces for Pandoc divs in markdown (`::: {.callout-note appearance="simple" icon=true}`). In Python generator f-strings, escape as double braces `{{...}}` to avoid Python string format syntax errors.
- **R Package Installation**: `bspm` is enabled in this environment. If installing user packages without sudo/dbus errors, disable `bspm` first:
  ```R
  bspm::disable(); install.packages("pkgname", repos="https://cloud.r-project.org")
  ```
- **CJK Font for ggplot2**: Chinese characters require the system font `Droid Sans Fallback` with `ragg::agg_png`. In ggplot2 themes, set `base_family = "Droid Sans Fallback"`.
- **Terra Raster Merging**: When merging multiple SpatRaster tiles in `terra`, pass a `sprc` collection: `merge(sprc(rasters))` instead of calling `merge()` directly on a list.
- **Remote Raster Access**: DLR WSF Evolution tiles stream over HTTP range requests via `/vsicurl/https://download.geoservice.dlr.de/WSF_EVO/files/...`. Always crop to city bounding box and write compressed GeoTIFFs (`COMPRESS=DEFLATE`).
- **GitHub Pages Requirement**: The compiled output lives in `docs/`. Both `docs/.nojekyll` and root `.nojekyll` must remain present so GitHub Pages does not ignore underscore directories like `site_libs`.
- **Large Data Gitignore**: `data/raw/*.geojson` and `data/raw/hotosm_railways/` are gitignored due to size (>300 MB). Store only aggregated geometries in `data/processed/*.rds` or `*.geojson`.
- **AGSL Google Drive Scans**: Scan URLs and mapping are stored in `data/processed/gdrive_agsl_scans.json` and `data/processed/city_agsl_scans_mapping.json`. When modifying city pages, preserve the `.agsl-box` callout and drive links.
- **UCSB ArcGIS Online Web Map**: Item ID `636bb82ea14944a5b719fc46cf055a53` and its feature server query attributes are cached in `data/processed/arcgis_study_cities.json` (providing `DianPing_ish_rank`, `RU_topos`, `ZH_CityAtlas`, and `planet`).
