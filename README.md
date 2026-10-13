# China Urban Growth Ratlas (1985–2015)
### 中国城市空间扩展图集 · 1985–2015

A geospatial **ratlas** (R-driven exploratory spatial atlas) tracking 30 years of physical urbanization across **47 Chinese cities** using open satellite-derived settlement data.

Built with **R**, `terra`, `sf`, `ggplot2`, and published as a modern static website via **Quarto**, configured for direct deployment to **GitHub Pages**.

---

## 🌟 Features

- **47 Diverse Cities**: Covering major provincial capitals, coastal Special Economic Zones (Shenzhen, Zhuhai, Xiamen), ancient Silk Road oases (Kashgar, Hotan, Wuwei, Lanzhou), northern industrial nodes, and northeast border outposts (Dandong, Hunchun).
- **Open Satellite Data**: Powered by the **DLR World Settlement Footprint Evolution (WSF Evolution)** 30-meter resolution annual settlement detection dataset (1985–2015) streamed via `/vsicurl/`.
- **Thematic Visual Suite per City**:
  1. **The Urban Growth Rings (Hero Poster)**: 4-epoch color-coded expansion morphology (Pre-1985, 1986–1995, 1996–2005, 2006–2015) with overlaid vector railway networks and bilingual CJK typography.
  2. **Small Multiples Progression**: 4 uniform-scale panels showing cumulative footprint expansion at 1985, 1995, 2005, and 2015.
  3. **Detailed Rail Network & Transit Corridors**: High-precision HOTOSM / OpenStreetMap railway layer displaying high-speed corridors (PDL), conventional rail trunk lines, and passenger station hubs over the 2015 built-up footprint.
  4. **Regional Location Inset**: Administrative context within China and its province.
  5. **30-Year Trajectory Curve**: Milestone surface area chart tracking physical expansion in $\text{km}^2$.
  6. **Archival Cartography & Wiki Resources**: One-click links to English Wikipedia, Chinese Wikipedia, Wikidata persistent QID entities, Wikimedia Commons map categories, and direct links to scanned historical maps.
- **Macro-Regional Analysis**: 6 regional chapters grouping cities by geographic and economic archetype.
- **GitHub Pages Ready**: Static website rendered into `docs/` with `.nojekyll`.

---

## 🚀 Deploying to GitHub Pages

1. **Initialize Git & Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: China Urban Growth Ratlas"
   git branch -M main
   git remote add origin https://github.com/<YOUR-USERNAME>/<YOUR-REPO-NAME>.git
   git push -u origin main
   ```

2. **Enable GitHub Pages**:
   - Go to your repository on GitHub: **Settings → Pages**.
   - Under **Build and deployment → Source**, select **Deploy from a branch**.
   - Under **Branch**, select `main` and folder `/docs`.
   - Click **Save**. Within 1–2 minutes, your website will be live at:
     `https://<YOUR-USERNAME>.github.io/<YOUR-REPO-NAME>/`

---

## 💻 Local Preview & Development

To preview the website locally in your browser:
```bash
quarto preview
```

To re-run the entire data ingestion, spatial cropping, map generation, and website build pipeline:
```bash
Rscript run_atlas.R
```

---

## 📂 Project Structure

```text
china-ratlas/
├── _quarto.yml              # Quarto website configuration (output-dir: docs)
├── styles.css               # Editorial dark theme stylesheet
├── index.qmd                # Master home page (national map, rankings, full table)
├── cities.qmd               # Searchable directory of all 47 cities
├── methodology.qmd          # Data sources, spatial processing & formulas
├── regions/                 # 6 macro-regional overview chapters
│   ├── coastal_south.qmd
│   ├── yangtze_basin.qmd
│   ├── yangtze_delta.qmd
│   ├── northern_plains.qmd
│   ├── northeast.qmd
│   └── western_frontier.qmd
├── cities/                  # 47 individual city spotlight documents
├── data/
│   ├── cities.json          # Master metadata (coordinates, bboxes, Chinese names)
│   ├── cities.csv           # Flat tabular metadata
│   ├── processed/
│   │   ├── wsf/             # Cached 30m GeoTIFFs (47 cropped city rasters)
│   │   ├── china_admin_layers.rds # Simplified GADM China boundaries
│   │   └── city_growth_stats.json # Calculated metrics (areas, multipliers, CAGR)
├── output/
│   ├── maps/                # 142 high-res maps (hero rings, small multiples, insets)
│   └── plots/               # 48 analytical charts (growth curves, rankings)
├── R/
│   ├── 02_fetch_and_crop_wsf.R     # Streaming & cropping WSF Evolution tiles
│   ├── 03_compute_growth_metrics.R # Spatial metric calculations
│   └── 04_generate_atlas_maps.R    # Batch map rendering (parallelized)
├── scripts/
│   ├── create_city_registry.py     # Metadata builder
│   └── generate_quarto_pages.py    # Automated Quarto page generator
├── docs/                    # Compiled static website (ready for GitHub Pages)
└── run_atlas.R              # One-command full pipeline runner
```

---

## 📊 Summary of Top Growth Cities (1985–2015)

| Rank | City | Chinese | Province | Region | 1985 Area | 2015 Area | Net Gain | Multiplier | CAGR |
|:---:|:---|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|
| #1 | **Heyuan** | 河源市 | Guangdong | Pearl River & South Coast | 15.2 km² | 136.5 km² | +121.3 km² | **9.01×** | 7.6% |
| #2 | **Chengdu** | 成都市 | Sichuan | Yangtze Basin & Central | 208.1 km² | 1,564.2 km² | +1,356.1 km² | **7.52×** | 7.0% |
| #3 | **Taizhou** | 泰州市 | Jiangsu | Yangtze Delta & East | 80.8 km² | 583.0 km² | +502.2 km² | **7.21×** | 6.8% |
| #4 | **Zhuhai** | 珠海市 | Guangdong | Pearl River & South Coast | 33.3 km² | 237.2 km² | +203.9 km² | **7.13×** | 6.8% |
| #5 | **Shenzhen** | 深圳市 | Guangdong | Pearl River & South Coast | 168.4 km² | 1,065.0 km² | +896.6 km² | **6.33×** | 6.3% |
| #6 | **Luzhou** | 泸州市 | Sichuan | Yangtze Basin & Central | 22.7 km² | 140.2 km² | +117.5 km² | **6.17×** | 6.2% |
| #7 | **Yangzhou** | 扬州市 | Jiangsu | Yangtze Delta & East | 99.0 km² | 601.0 km² | +502.0 km² | **6.07×** | 6.2% |
| #8 | **Weihai** | 威海市 | Shandong | Yellow River & North Plain | 32.9 km² | 179.9 km² | +147.0 km² | **5.46×** | 5.8% |
| #9 | **Hohhot** | 呼和浩特市 | Inner Mongolia | Western Frontier & Steppe | 68.9 km² | 349.4 km² | +280.5 km² | **5.07×** | 5.6% |
| #10 | **Jining** | 济宁市 | Shandong | Yellow River & North Plain | 77.4 km² | 391.1 km² | +313.7 km² | **5.05×** | 5.5% |

---

## 📜 Comprehensive Data Sources, Citations & Attributions

This project integrates five primary geospatial and demographic datasets from authoritative open web repositories:

### 1. DLR World Settlement Footprint Evolution (WSF Evolution)
- **Custodian**: German Aerospace Center (Deutsches Zentrum für Luft- und Raumfahrt; DLR), Earth Observation Center (EOC).
- **Resolution & Scope**: 30-meter global annual settlement detection grid (1985–2015) derived from joint multi-decadal optical (Landsat-5/7/8) and radar (ERS-1/2, Sentinel-1) satellite imagery.
- **Data Access**: [German Aerospace Center (DLR) Geoservice](https://download.geoservice.dlr.de/WSF_EVO/) via GDAL `/vsicurl/` range requests.
- **License**: Creative Commons Attribution 4.0 International (CC-BY 4.0).
- **Academic Citations**:
  - Marconcini, M., Metz, A., Üreyen, S., Palacios-Lopez, D., Hanke, W., Bachofer, F., Zeidler, J., Esch, T., Gorelick, N., Kakarla, A., Paganini, M., & Strano, E. (2020). *Outlining where humans live, the World Settlement Footprint 2015.* **Scientific Data**, 7(1), 242. [https://doi.org/10.1038/s41597-020-00580-5](https://doi.org/10.1038/s41597-020-00580-5)
  - Marconcini, M., Metz, A., Zeidler, J., & Esch, T. (2021). *The World Settlement Footprint Evolution—30 Years of Growth.* **Remote Sensing of Environment**, 255, 112282.

### 2. HOTOSM Railways of China Dataset
- **Custodian**: Humanitarian OpenStreetMap Team (HOTOSM) & United Nations Office for the Coordination of Humanitarian Affairs (UN OCHA).
- **Platform**: Humanitarian Data Exchange (HDX).
- **Data Access**: [Railways of China Dataset on HDX](https://data.humdata.org/dataset/hotosm_chn_railways).
- **Scope**: Complete OpenStreetMap railway extract for China (>430,000 vector segments) filtered and aggregated into 194 High-Speed Rail corridors.
- **License**: Open Data Commons Open Database License (ODbL 1.0) by OpenStreetMap contributors.

### 3. ArcGIS Online Big Cities Points Layer
- **Custodian**: Esri / ArcGIS Online Feature Services.
- **Endpoint**: [`big_cities_points` FeatureServer](https://services1.arcgis.com/4TXrdeWh0RyCqPgB/arcgis/rest/services/big_cities_points/FeatureServer).
- **Scope**: 184 major Chinese urban nodes with national urban hierarchy rankings (`rank` 1 to 200).
- **Role**: Validates sample selection, confirms exclusion of tier-1 megacities, and assigns national hierarchy tiers.

### 4. Seventh National Population Census of China (第七次全国人口普查 / 七普 2020)
- **Custodian**: National Bureau of Statistics of China (中华人民共和国国家统计局; NBS), Beijing, China.
- **Scope**: Permanent resident population (*常住人口*) as of November 1, 2020, defining the primary sorting order of the ratlas (#1 Chengdu 20.94M to #47 Hunchun 0.24M).
- **Citation**: Office of the Leading Group of the State Council for the Seventh National Population Census. (2021). *Major Figures on 2020 Population Census of China.* China Statistics Press. [http://www.stats.gov.cn/](http://www.stats.gov.cn/)

### 5. GADM Database of Global Administrative Areas
- **Custodian**: University of California, Davis (Department of Environmental Science and Policy).
- **Version**: GADM 4.1 ([https://gadm.org/](https://gadm.org/)).
- **Citation**: Hijmans, R. J., Garcia, N., & Wieczorek, J. (2022). *GADM Database of Global Administrative Areas, Version 4.1*. University of California, Davis.

### 6. Core Software Stack
- **R Environment**: R Core Team (2026). R v4.6.1.
- **Spatial Analysis**: `terra` (Hijmans, 2024), `sf` (Pebesma, 2018), `tidyterra` (Hernangómez, 2023).
- **Graphics**: `ggplot2` (Wickham, 2016), `patchwork` (Pedersen, 2024), `ragg`.
- **CJK Typography**: `Droid Sans Fallback` (Google Android Open Source Project).
- **Web Compilation**: Quarto (Posit Software).
