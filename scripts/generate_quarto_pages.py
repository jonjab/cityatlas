import json, os

with open("data/processed/city_growth_stats.json", "r", encoding="utf-8") as f:
    cities = json.load(f)

print(f"Loaded {len(cities)} cities for Quarto page generation.")

# Group cities by region
regions_map = {
    "coastal_south": {
        "title": "Pearl River Delta & South Coast",
        "title_zh": "珠江三角洲与华南沿海",
        "desc": "China's economic vanguard: Special Economic Zones, deep-water ports, and massive industrial expansion across Guangdong, Fujian, and Hainan.",
        "cities": []
    },
    "yangtze_basin": {
        "title": "Yangtze Basin & Central Metropolises",
        "title_zh": "长江流域与华中特大城市",
        "desc": "Mega-hubs along the Yangtze River corridor and Sichuan Basin, experiencing massive inland infrastructure and concentric metropolitan sprawl.",
        "cities": []
    },
    "yangtze_delta": {
        "title": "Yangtze Delta & East",
        "title_zh": "长三角与华东城镇群",
        "desc": "The ancient water towns transformed into interconnected manufacturing clusters, high-tech manufacturing, and logistics hubs.",
        "cities": []
    },
    "northern_plains": {
        "title": "Yellow River & North Plain",
        "title_zh": "黄河流域与华北平原",
        "desc": "Industrial cores, railway nodes, and Bohai Rim industrial cities expanding across the great alluvial plain.",
        "cities": []
    },
    "northeast": {
        "title": "Northeast Rust Belt",
        "title_zh": "东北老工业基地与边境口岸",
        "desc": "Heavy industry cradles, mining cities, and strategic border gateway outposts in Heilongjiang, Jilin, and Liaoning.",
        "cities": []
    },
    "western_frontier": {
        "title": "Western Frontier & Steppe",
        "title_zh": "西部边疆、丝路绿洲与草原",
        "desc": "Ancient Silk Road oases, western capitals, and northern grassland centers bounded by mountains and deserts.",
        "cities": []
    }
}

for c in cities:
    r = c["region"]
    if "Pearl River" in r or "South Coast" in r:
        regions_map["coastal_south"]["cities"].append(c)
    elif "Yangtze Basin" in r or "Central" in r:
        regions_map["yangtze_basin"]["cities"].append(c)
    elif "Yangtze Delta" in r or "East" in r:
        regions_map["yangtze_delta"]["cities"].append(c)
    elif "Yellow River" in r or "North Plain" in r:
        regions_map["northern_plains"]["cities"].append(c)
    elif "Northeast" in r:
        regions_map["northeast"]["cities"].append(c)
    else:
        regions_map["western_frontier"]["cities"].append(c)

os.makedirs("cities", exist_ok=True)
os.makedirs("regions", exist_ok=True)

# ------------------------------------------------------------------------------
# 1. Generate Individual City Pages
# ------------------------------------------------------------------------------
for idx, c in enumerate(cities):
    c_id = c["id"]
    prev_c = cities[idx - 1] if idx > 0 else cities[-1]
    next_c = cities[idx + 1] if idx < len(cities) - 1 else cities[0]
    
    # Identify regional file
    reg_file = "western_frontier.qmd"
    for rk, rv in regions_map.items():
        if any(item["id"] == c_id for item in rv["cities"]):
            reg_file = f"{rk}.qmd"
            break

    qmd_content = f"""---
title: "{c['name_en']} ({c['name_zh']})"
subtitle: "{c['pinyin']} · {c['province_en']} ({c['province_zh']}) · {c['region']}"
format:
  html:
    toc: true
---

::: {{.hero-banner}}
<div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
  <div>
    <h1 style="color: #ffffff; margin-bottom: 0.25rem;">{c['name_en']} <span style="color: #f59e0b; font-weight: normal;">{c['name_zh']}</span></h1>
    <p style="color: #94a3b8; font-size: 1.1rem; margin: 0;">{c['pinyin']} · {c['province_en']} Province · National Rank: <strong>#{c['rank_multiplier']}</strong> of 47</p>
  </div>
  <div style="text-align: right;">
    <span class="metric-badge badge-gold" style="font-size: 1.1rem; padding: 0.5rem 1rem;">{c['growth_multiple']}× Multiplier</span>
  </div>
</div>
:::

## Key Expansion Indicators (1985–2015)

::: {{.metric-grid}}
::: {{.metric-card}}
::: {{.metric-label}}
1985 Baseline Area
:::
::: {{.metric-val}}
{c['area_1985']} <span style="font-size: 1rem; color: #94a3b8;">km²</span>
:::
:::

::: {{.metric-card}}
::: {{.metric-label}}
2015 Urban Footprint
:::
::: {{.metric-val}}
{c['area_2015']} <span style="font-size: 1rem; color: #94a3b8;">km²</span>
:::
:::

::: {{.metric-card}}
::: {{.metric-label}}
Net Surface Gain
:::
::: {{.metric-val}}
+{c['net_gain_km2']} <span style="font-size: 1rem; color: #94a3b8;">km²</span>
:::
:::

::: {{.metric-card}}
::: {{.metric-label}}
Growth Multiple
:::
::: {{.metric-val}}
{c['growth_multiple']}×
:::
:::

::: {{.metric-card}}
::: {{.metric-label}}
Annual Growth (CAGR)
:::
::: {{.metric-val}}
{c['cagr_pct']}%
:::
:::
:::

---

## 1. The Urban Growth Rings (1985–2015)

The primary cartographic poster below visualizes the physical expansion rings of **{c['name_en']}**, partitioned into four milestone eras:

- <span style="color: #F59E0B; font-weight: bold;">● Pre-1985</span>: Historic core and initial post-1949 development.
- <span style="color: #EF4444; font-weight: bold;">● 1986–1995</span>: Early reform, opening up, and Deng Xiaoping's southern tour.
- <span style="color: #06B6D4; font-weight: bold;">● 1996–2005</span>: WTO entry, export boom, and new industrial development zones.
- <span style="color: #10B981; font-weight: bold;">● 2006–2015</span>: High-speed rail expansion, modern new towns (*xinqu*), and peri-urban consolidation.

::: {{.map-container}}
!['The Urban Growth Rings: {c['name_en']}'](../output/maps/{c_id}_hero.png)
:::

---

## 2. Small Multiples: 4-Epoch Footprint Evolution

Comparative uniform-scale footprint maps isolating the cumulative urbanized surface across the four key epochs:

::: {{.map-container}}
!['Small Multiples Footprint Progression: {c['name_en']}'](../output/maps/{c_id}_small_multiples.png)
:::

---

## 3. Geographical Context & Growth Trajectory

:::: {{.columns}}

::: {{.column width="48%"}}
### National Location
::: {{.map-container}}
!['Regional Inset: {c['name_en']}'](../output/maps/{c_id}_context.png)
:::
:::

::: {{.column width="4%"}}
:::

::: {{.column width="48%"}}
### 30-Year Expansion Curve
::: {{.map-container}}
!['Expansion Trajectory: {c['name_en']}'](../output/plots/{c_id}_trajectory.png)
:::
:::

::::

---

## 4. 5-Year Milestone Chronology

The table below catalogs the cumulative built-up surface area of {c['name_en']} at 5-year intervals:

| Milestone Year | Urban Footprint (km²) | Growth vs. 1985 Baseline | Share of 2015 Footprint |
|:---:|:---:|:---:|:---:|
| **1985** | {c['area_1985']} km² | 1.00× (Baseline) | {round(c['area_1985'] / max(c['area_2015'], 0.1) * 100, 1)}% |
| **1990** | {c['area_1990']} km² | {round(c['area_1990'] / max(c['area_1985'], 0.1), 2)}× | {round(c['area_1990'] / max(c['area_2015'], 0.1) * 100, 1)}% |
| **1995** | {c['area_1995']} km² | {round(c['area_1995'] / max(c['area_1985'], 0.1), 2)}× | {round(c['area_1995'] / max(c['area_2015'], 0.1) * 100, 1)}% |
| **2000** | {c['area_2000']} km² | {round(c['area_2000'] / max(c['area_1985'], 0.1), 2)}× | {round(c['area_2000'] / max(c['area_2015'], 0.1) * 100, 1)}% |
| **2005** | {c['area_2005']} km² | {round(c['area_2005'] / max(c['area_1985'], 0.1), 2)}× | {round(c['area_2005'] / max(c['area_2015'], 0.1) * 100, 1)}% |
| **2010** | {c['area_2010']} km² | {round(c['area_2010'] / max(c['area_1985'], 0.1), 2)}× | {round(c['area_2010'] / max(c['area_2015'], 0.1) * 100, 1)}% |
| **2015** | {c['area_2015']} km² | **{c['growth_multiple']}×** | 100.0% |

---

<div style="display: flex; justify-content: space-between; margin-top: 2rem; padding: 1rem; background: #111827; border-radius: 8px;">
  <a href="{prev_c['id']}.html" style="color: #38bdf8; text-decoration: none;">← Previous: {prev_c['name_en']} ({prev_c['name_zh']})</a>
  <a href="../regions/{reg_file.replace('.qmd', '.html')}" style="color: #f59e0b; text-decoration: none;">↑ {c['region']}</a>
  <a href="{next_c['id']}.html" style="color: #38bdf8; text-decoration: none;">Next: {next_c['name_en']} ({next_c['name_zh']}) →</a>
</div>
"""
    with open(f"cities/{c_id}.qmd", "w", encoding="utf-8") as f:
        f.write(qmd_content.strip() + "\n")

print(f"Generated 47 individual city QMD documents in cities/.")

# ------------------------------------------------------------------------------
# 2. Generate Regional Pages
# ------------------------------------------------------------------------------
for rk, rv in regions_map.items():
    r_cities = sorted(rv["cities"], key=lambda x: x["growth_multiple"], reverse=True)
    
    rows = ""
    city_links = ""
    for c in r_cities:
        rows += f"""| [{c['name_en']}](../cities/{c['id']}.html) | {c['name_zh']} | {c['province_en']} | {c['area_1985']} km² | {c['area_2015']} km² | +{c['net_gain_km2']} km² | **{c['growth_multiple']}×** | {c['cagr_pct']}% | #{c['rank_multiplier']} |\n"""
        
        city_links += f"""
::: {{.region-card}}
### [{c['name_en']} ({c['name_zh']})](../cities/{c['id']}.html)
**{c['province_en']} Province** · 30-Year Multiplier: <strong style="color: #f59e0b;">{c['growth_multiple']}×</strong> (#{c['rank_multiplier']} Nationally)

- **1985 Footprint**: {c['area_1985']} km²
- **2015 Footprint**: {c['area_2015']} km² (Net expansion: +{c['net_gain_km2']} km²)
- **Compound Annual Growth Rate**: {c['cagr_pct']}%/year

[View Maps & Visual Suite →](../cities/{c['id']}.html)
:::
"""

    reg_content = f"""---
title: "{rv['title']}"
subtitle: "{rv['title_zh']} · {len(r_cities)} Cities"
format:
  html:
    toc: true
---

::: {{.hero-banner}}
<h1 style="color: #ffffff; margin-bottom: 0.5rem;">{rv['title']} <span style="color: #f59e0b;">{rv['title_zh']}</span></h1>
<p style="color: #cbd5e1; font-size: 1.1rem;">{rv['desc']}</p>
:::

## Regional Comparison Table

| City | Chinese | Province | 1985 Area | 2015 Area | Net Gain | Multiplier | CAGR | National Rank |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
{rows}

---

## Member City Profiles

{city_links}
"""
    with open(f"regions/{rk}.qmd", "w", encoding="utf-8") as f:
        f.write(reg_content.strip() + "\n")

print("Generated 6 regional QMD documents in regions/.")

# ------------------------------------------------------------------------------
# 3. Generate All Cities Directory (cities.qmd)
# ------------------------------------------------------------------------------
all_rows = ""
for c in cities:
    all_rows += f"""| #{c['rank_multiplier']} | [{c['name_en']}](cities/{c['id']}.html) | {c['name_zh']} | {c['province_en']} | {c['region']} | {c['area_1985']} km² | {c['area_2015']} km² | +{c['net_gain_km2']} km² | **{c['growth_multiple']}×** | {c['cagr_pct']}% |\n"""

cities_qmd = f"""---
title: "All 47 Cities Directory"
subtitle: "Comprehensive 30-Year Urban Growth Inventory (1985–2015)"
format:
  html:
    toc: false
---

::: {{.hero-banner}}
<h1 style="color: #ffffff; margin-bottom: 0.5rem;">The 47 Cities of the Ratlas</h1>
<p style="color: #cbd5e1;">A complete catalogue of all 47 cities analyzed in this project, ranked by 30-year physical expansion multiplier.</p>
:::

| Rank | City | Chinese | Province | Region | 1985 Area | 2015 Area | Net Gain | Multiplier | CAGR |
|:---:|:---|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|
{all_rows}
"""
with open("cities.qmd", "w", encoding="utf-8") as f:
    f.write(cities_qmd.strip() + "\n")

# ------------------------------------------------------------------------------
# 4. Generate Methodology Page (methodology.qmd)
# ------------------------------------------------------------------------------
methodology_qmd = """---
title: "Data & Methodology"
subtitle: "Geospatial Data Sources, Processing Pipeline, and Analytical Framework"
format:
  html:
    toc: true
---

::: {.hero-banner}
<h1 style="color: #ffffff; margin-bottom: 0.5rem;">Analytical Methodology</h1>
<p style="color: #cbd5e1;">How this ratlas ingests, processes, and cartographically renders 30 years of satellite-detected urban expansion across China.</p>
:::

## 1. Primary Data Source: DLR WSF Evolution

The physical urban growth data in this project is driven by the **World Settlement Footprint Evolution (WSF Evolution)** dataset, produced by the **German Aerospace Center (DLR)**:

- **Spatial Resolution**: 30 meters per pixel, derived from joint multi-decadal analysis of **Landsat-5, Landsat-7, and Landsat-8** optical imagery, integrated with radar and digital elevation datasets.
- **Temporal Coverage**: 1985 to 2015 (30-year span).
- **Pixel Semantics**: Each pixel value encodes the exact calendar year ($1985 \le \text{year} \le 2015$) in which human settlement was first detected. Value `0` represents non-urban surfaces (natural vegetation, bare land, agriculture, or water). Value `1985` represents human settlements already established by or prior to 1985.
- **Open Web Retrieval**: Retrieved directly from DLR's open data servers (`download.geoservice.dlr.de`) using GDAL virtual file streaming (`/vsicurl/`) and R's `terra` package.

## 2. Administrative Geodatabase & Extents

- **GADM 4.1 (Database of Global Administrative Areas)**: Provided level 0 (national outline), level 1 (provincial boundaries), and level 2 (prefectural boundaries).
- **Centroids & Analysis Radii**: Urban core extents were established for each city based on high-density metropolitan boundaries, ranging from 12 km to 30 km radius depending on city tier and metropolitan scale.
- **Coordinate Reference Systems**: Base data in WGS 84 (EPSG:4326), with surface area calculations performed using ellipsoidal pixel geometry (`terra::cellSize(unit = "km")`) to eliminate high-latitude area distortion.

## 3. Four Landmark Urban Development Epochs

Urban expansion in modern China has unfolded in distinct historical waves:

1. **Pre-1985 Core** (`#F59E0B` · Amber Gold):
   The pre-reform base urban footprint. This includes ancient historical city cores and the industrial settlements constructed during the early Five-Year Plans (1949–1980).
2. **1986–1995 Wave** (`#EF4444` · Crimson Coral):
   Deng Xiaoping's 1992 Southern Tour (*Nanxun*), the launch of Special Economic Zones (SEZs), and the initial surge of rural-to-urban industrialization.
3. **1996–2005 Wave** (`#06B6D4` · Electric Cyan):
   China's 2001 accession to the World Trade Organization (WTO), the emergence of the "Factory of the World", highway grid expansion, and initial high-tech development zones.
4. **2006–2015 Wave** (`#10B981` · Emerald Green):
   The High-Speed Rail (HSR) construction boom, the Western Development Strategy (*Xibu Da Kaifa*), massive State-level New Areas (*Guojiaji Xinqu*), and metropolitan amalgamation.

## 4. Quantitative Metrics

For each city, the following metrics are computed:

- **Cumulative Built-Up Area ($A_t$)**: Total surface area in $\text{km}^2$ occupied by detected settlements at year $t$.
- **Net Spatial Gain ($\Delta A$)**: $A_{2015} - A_{1985}$.
- **30-Year Growth Multiple ($M$)**: $A_{2015} / A_{1985}$.
- **Compound Annual Growth Rate (CAGR)**: $\left(\frac{A_{2015}}{A_{1985}}\right)^{1/30} - 1$.

## 5. Cartographic Stack & Tools

- **Language & Runtime**: R (v4.6.1) & Python 3
- **Spatial Processing**: `terra` (v1.9), `sf` (v1.0), `tidyterra`
- **Visualization**: `ggplot2`, `patchwork`, `ragg`
- **Typography**: CJK rendering via system font `Droid Sans Fallback` with bilingual typesetting
- **Publishing**: Quarto static site compiler deployed directly to GitHub Pages
"""
with open("methodology.qmd", "w", encoding="utf-8") as f:
    f.write(methodology_qmd.strip() + "\n")

# ------------------------------------------------------------------------------
# 5. Generate Home Page (index.qmd)
# ------------------------------------------------------------------------------
index_qmd = f"""---
title: "China Urban Growth Ratlas (1985–2015)"
subtitle: "A Geospatial Exploration of 30 Years of Physical Expansion Across 47 Chinese Metropolises"
format:
  html:
    toc: true
---

::: {{.hero-banner}}
<div style="max-width: 900px;">
  <h1 class="hero-title">China Urban Growth Ratlas</h1>
  <h2 style="color: #f59e0b; font-size: 1.5rem; margin-top: -0.25rem; margin-bottom: 1rem;">中国城市空间扩展图集 · 1985–2015</h2>
  <p class="hero-subtitle">
    Between 1985 and 2015, the People's Republic of China underwent the largest, fastest physical urbanization process in human history. 
    This ratlas maps the spatial morphology, expansion rings, and quantitative growth trajectories across <strong>47 diverse Chinese cities</strong>—from southern coastal manufacturing hubs and ancient Silk Road oases to central megacities and northeast border outposts.
  </p>
  <div style="display: flex; gap: 1rem; margin-top: 1.5rem; flex-wrap: wrap;">
    <a href="cities.html" class="btn btn-primary" style="background: #0284c7; border: none; padding: 0.6rem 1.25rem; font-weight: 600;">Browse All 47 Cities →</a>
    <a href="methodology.html" class="btn btn-secondary" style="background: #1e293b; color: #cbd5e1; border: 1px solid #334155; padding: 0.6rem 1.25rem;">Methodology & Data</a>
  </div>
</div>
:::

## Key Findings & National Overview

::: {{.metric-grid}}
::: {{.metric-card}}
::: {{.metric-label}}
Total Cities Analyzed
:::
::: {{.metric-val}}
47
:::
:::

::: {{.metric-card}}
::: {{.metric-label}}
Median Growth Multiple
:::
::: {{.metric-val}}
4.1×
:::
:::

::: {{.metric-card}}
::: {{.metric-label}}
Peak Growth Multiple
:::
::: {{.metric-val}}
9.0×
:::
<div style="font-size: 0.8rem; color: #f59e0b;">Heyuan (河源市)</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
Peak Area Expansion
:::
::: {{.metric-val}}
+1,356 <span style="font-size: 1rem;">km²</span>
:::
<div style="font-size: 0.8rem; color: #f59e0b;">Chengdu (成都市)</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
Satellite Data Resolution
:::
::: {{.metric-val}}
30 <span style="font-size: 1rem;">meters</span>
:::
:::
:::

---

## National Urban Expansion Map

The map below displays all 47 cities in the ratlas across China, sized by their **2015 built-up area ($km^2$)** and colored by their **30-year growth multiplier**:

::: {{.map-container}}
!['China Urban Growth Ratlas National Overview'](output/maps/china_overview_map.png)
:::

---

## National Growth Multiplier Rankings

Which cities experienced the highest relative spatial expansion between 1985 and 2015?

::: {{.map-container}}
!['Top 25 Cities by 30-Year Urban Growth Multiple'](output/plots/national_growth_ranking.png)
:::

---

## Regional Explorations

Explore the atlas by geographic macro-regions:

::: {{.columns}}

::: {{.column width="32%"}}
::: {{.region-card}}
### [Pearl River & South Coast](regions/coastal_south.html)
Special Economic Zones, export engines, and coastal reclaimers.
- **Cities**: Shenzhen, Zhuhai, Xiamen, Haikou, Taishan, Heyuan
[Explore Region →](regions/coastal_south.html)
:::
:::

::: {{.column width="32%"}}
::: {{.region-card}}
### [Yangtze Basin & Central](regions/yangtze_basin.html)
Inland megacities and riverine industrial corridors.
- **Cities**: Chengdu, Wuhan, Luzhou, Yichang, Nanchang, Zhangjiajie
[Explore Region →](regions/yangtze_basin.html)
:::
:::

::: {{.column width="32%"}}
::: {{.region-card}}
### [Yangtze Delta & East](regions/yangtze_delta.html)
Interconnected manufacturing clusters and canal towns.
- **Cities**: Taizhou, Yangzhou, Wuhu, Huangshan, Lianyungang
[Explore Region →](regions/yangtze_delta.html)
:::
:::

:::

::: {{.columns}}

::: {{.column width="32%"}}
::: {{.region-card}}
### [Yellow River & North Plain](regions/northern_plains.html)
Heavy industrial centers across the agricultural heartland.
- **Cities**: Jinan, Zhengzhou, Baoding, Shijiazhuang, Zibo...
[Explore Region →](regions/northern_plains.html)
:::
:::

::: {{.column width="32%"}}
::: {{.region-card}}
### [Northeast Rust Belt](regions/northeast.html)
Early industrial powerhouses and international border gateways.
- **Cities**: Harbin, Dandong, Fuxin, Panjin, Tieling, Hunchun...
[Explore Region →](regions/northeast.html)
:::
:::

::: {{.column width="32%"}}
::: {{.region-card}}
### [Western Frontier & Steppe](regions/western_frontier.html)
Silk Road oasis towns, highland capitals, and desert gateways.
- **Cities**: Xi'an, Lanzhou, Urumqi, Kashgar, Hotan, Hohhot...
[Explore Region →](regions/western_frontier.html)
:::
:::

:::

---

## Complete 47-City Master Index

| Rank | City | Chinese | Province | Region | 1985 Area | 2015 Area | Net Gain | Multiplier | CAGR |
|:---:|:---|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|
{all_rows}

---

::: {{.caption-box}}
**China Urban Growth Ratlas** · Built with R (`terra`, `sf`, `ggplot2`, `tidyterra`, `patchwork`) and Quarto. Data: German Aerospace Center (DLR) World Settlement Footprint Evolution (30m) & GADM 4.1.
:::
"""

with open("index.qmd", "w", encoding="utf-8") as f:
    f.write(index_qmd.strip() + "\n")

print("Generated index.qmd, cities.qmd, and methodology.qmd successfully!")
