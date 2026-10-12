import json, os

with open("data/processed/city_growth_stats.json", "r", encoding="utf-8") as f:
    cities = json.load(f)

# Sort strictly by population rank (#1 to #47)
cities = sorted(cities, key=lambda x: x["rank_population"])

print(f"Loaded {len(cities)} cities ordered by population rank.")

# Regional mapping
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
# 1. Generate Individual City Pages (Using raw {=html} blocks)
# ------------------------------------------------------------------------------
for idx, c in enumerate(cities):
    c_id = c["id"]
    prev_c = cities[idx - 1] if idx > 0 else cities[-1]
    next_c = cities[idx + 1] if idx < len(cities) - 1 else cities[0]
    
    reg_file = "western_frontier.qmd"
    for rk, rv in regions_map.items():
        if any(item["id"] == c_id for item in rv["cities"]):
            reg_file = f"{rk}.qmd"
            break

    hero_block = f"""```{{=html}}
<div class="hero-banner">
  <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
    <div>
      <h1 style="color: #ffffff; margin-bottom: 0.25rem;">{c['name_en']} <span style="color: #f59e0b; font-weight: normal;">{c['name_zh']}</span></h1>
      <p style="color: #94a3b8; font-size: 1.1rem; margin: 0;">{c['pinyin']} · {c['province_en']} ({c['province_zh']}) · {c['region']}</p>
      <p style="color: #cbd5e1; font-size: 0.95rem; margin-top: 0.35rem;">Population: <strong>{c['pop_million']} Million</strong> (2020 Census) · National Rank: <strong>#{c['rank_population']}</strong> of 47</p>
    </div>
    <div style="text-align: right;">
      <span class="metric-badge badge-gold" style="font-size: 1.1rem; padding: 0.5rem 1rem;">{c['growth_multiple']}× Growth Multiplier</span>
    </div>
  </div>
</div>
```"""

    footer_nav = f"""```{{=html}}
<div style="display: flex; justify-content: space-between; margin-top: 2rem; padding: 1rem; background: #111827; border-radius: 8px;">
  <a href="{prev_c['id']}.html" style="color: #38bdf8; text-decoration: none;">← Prev: {prev_c['name_en']} ({prev_c['pop_million']}M)</a>
  <a href="../regions/{reg_file.replace('.qmd', '.html')}" style="color: #f59e0b; text-decoration: none;">↑ {c['region']}</a>
  <a href="{next_c['id']}.html" style="color: #38bdf8; text-decoration: none;">Next: {next_c['name_en']} ({next_c['pop_million']}M) →</a>
</div>
```"""

    qmd_content = f"""---
title: "{c['name_en']} ({c['name_zh']})"
subtitle: "Population: {c['pop_million']}M · 30-Year Growth: {c['growth_multiple']}× · {c['province_en']}"
format:
  html:
    toc: true
---

{hero_block}

## Key Urban Expansion Indicators

::: {{.metric-grid}}
::: {{.metric-card}}
::: {{.metric-label}}
2020 Population
:::
::: {{.metric-val}}
{c['pop_million']} <span style="font-size: 1rem; color: #94a3b8;">M</span>
:::
<div style="font-size: 0.8rem; color: #38bdf8;">Rank #{c['rank_population']} of 47</div>
:::

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
<div style="font-size: 0.8rem; color: #10b981;">+{c['net_gain_km2']} km²</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
Growth Multiple
:::
::: {{.metric-val}}
{c['growth_multiple']}×
:::
<div style="font-size: 0.8rem; color: #f59e0b;">Rank #{c['rank_multiplier']} of 47</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
Annual Growth (CAGR)
:::
::: {{.metric-val}}
{c['cagr_pct']}%
:::
<div style="font-size: 0.8rem; color: #94a3b8;">1985–2015</div>
:::
:::

---

## 1. The Urban Growth Rings (1985–2015)

The cartographic poster below maps the physical settlement rings of **{c['name_en']}** across four historical development epochs:

- <span style="color: #F59E0B; font-weight: bold;">● Pre-1985 Core</span>: Historic urban core and initial post-1949 industrial settlements.
- <span style="color: #EF4444; font-weight: bold;">● 1986–1995 Wave</span>: Early reform, opening up, and Deng Xiaoping's 1992 Southern Tour (*Nanxun*).
- <span style="color: #06B6D4; font-weight: bold;">● 1996–2005 Wave</span>: WTO entry, export industrialization, and new development zones (*Kaifaqu*).
- <span style="color: #10B981; font-weight: bold;">● 2006–2015 Wave</span>: High-speed rail expansion, modern new cities (*Xinqu*), and peri-urban consolidation.

::: {{.map-container}}
!['The Urban Growth Rings: {c['name_en']}'](../output/maps/{c_id}_hero.png)
:::

---

## 2. Small Multiples: 4-Epoch Footprint Progression

Uniform-scale physical footprint progression maps tracking built-up settlement expansion over time:

::: {{.map-container}}
!['Small Multiples Footprint Progression: {c['name_en']}'](../output/maps/{c_id}_small_multiples.png)
:::

---

## 3. Geographical Location & Growth Trajectory

:::: {{.columns}}

::: {{.column width="48%"}}
### Location in China
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

{footer_nav}
"""
    with open(f"cities/{c_id}.qmd", "w", encoding="utf-8") as f:
        f.write(qmd_content.strip() + "\n")

print(f"Generated 47 individual city QMD documents in cities/ using raw html blocks.")

# ------------------------------------------------------------------------------
# 2. Generate Regional Pages (Sorted by Population)
# ------------------------------------------------------------------------------
for rk, rv in regions_map.items():
    r_cities = sorted(rv["cities"], key=lambda x: x["rank_population"])
    
    rows = ""
    city_links = ""
    for c in r_cities:
        rows += f"""| #{c['rank_population']} | [{c['name_en']}](../cities/{c['id']}.html) | {c['name_zh']} | {c['province_en']} | **{c['pop_million']}M** | {c['area_1985']} km² | {c['area_2015']} km² | +{c['net_gain_km2']} km² | **{c['growth_multiple']}×** | {c['cagr_pct']}% |\n"""
        
        city_links += f"""
::: {{.region-card}}
### [{c['name_en']} ({c['name_zh']})](../cities/{c['id']}.html)
**{c['province_en']} Province** · Population: <strong style="color: #38bdf8;">{c['pop_million']} Million</strong> (Rank #{c['rank_population']}) · 30-Year Multiplier: <strong style="color: #f59e0b;">{c['growth_multiple']}×</strong>

- **1985 Footprint**: {c['area_1985']} km²
- **2015 Footprint**: {c['area_2015']} km² (Net expansion: +{c['net_gain_km2']} km²)
- **Compound Annual Growth Rate**: {c['cagr_pct']}%/year

[View Maps & Visual Suite →](../cities/{c['id']}.html)
:::
"""

    reg_hero = f"""```{{=html}}
<div class="hero-banner">
  <h1 style="color: #ffffff; margin-bottom: 0.5rem;">{rv['title']} <span style="color: #f59e0b;">{rv['title_zh']}</span></h1>
  <p style="color: #cbd5e1; font-size: 1.1rem; margin: 0;">{rv['desc']}</p>
</div>
```"""

    reg_content = f"""---
title: "{rv['title']}"
subtitle: "{rv['title_zh']} · {len(r_cities)} Cities Ordered by Population"
format:
  html:
    toc: true
---

{reg_hero}

## Regional Member Cities (Ranked by Population)

| Pop Rank | City | Chinese | Province | Population | 1985 Area | 2015 Area | Net Gain | Multiplier | CAGR |
|:---:|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
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
    all_rows += f"""| #{c['rank_population']} | [{c['name_en']}](cities/{c['id']}.html) | {c['name_zh']} | {c['province_en']} | {c['region']} | **{c['pop_million']}M** | {c['area_1985']} km² | {c['area_2015']} km² | +{c['net_gain_km2']} km² | **{c['growth_multiple']}×** | {c['cagr_pct']}% |\n"""

cities_qmd = f"""---
title: "All 47 Cities Directory"
subtitle: "Complete 30-Year Urban Growth Inventory Ordered by Population (2020 Census)"
format:
  html:
    toc: false
---

```{{=html}}
<div class="hero-banner">
  <h1 style="color: #ffffff; margin-bottom: 0.5rem;">The 47 Cities of the Ratlas</h1>
  <p style="color: #cbd5e1; margin: 0;">Complete inventory of all 47 cities analyzed in this project, ranked from largest to smallest population based on the 7th National Population Census (七普 2020).</p>
</div>
```

::: {{.callout-note appearance="simple"}}
**Selection Note**: Cities were selected to exclude China's tier-1 superstar megacities (Beijing, Shanghai, Guangzhou, Chongqing, Tianjin) to examine dynamic provincial capitals, regional economic drivers, and specialized border gateways.
:::

| Pop Rank | City | Chinese | Province | Region | Population | 1985 Area | 2015 Area | Net Gain | Multiplier | CAGR |
|:---:|:---|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
{all_rows}
"""
with open("cities.qmd", "w", encoding="utf-8") as f:
    f.write(cities_qmd.strip() + "\n")

# ------------------------------------------------------------------------------
# 4. Generate Methodology Page (methodology.qmd)
# ------------------------------------------------------------------------------
methodology_qmd = r"""---
title: "Data & Methodology"
subtitle: "Geospatial Data Sources, Processing Pipeline, High-Speed Rail Integration, and Population Metrics"
format:
  html:
    toc: true
---

```{=html}
<div class="hero-banner">
  <h1 style="color: #ffffff; margin-bottom: 0.5rem;">Analytical Methodology</h1>
  <p style="color: #cbd5e1; margin: 0;">How this ratlas ingests, processes, and cartographically renders 30 years of satellite-detected urban expansion, High-Speed Rail networks, and census populations across China.</p>
</div>
```

::: {.callout-important appearance="simple"}
## Scope & Sample Selection Note: Excluding Tier-1 Megacities
The 47 cities in this atlas were deliberately selected to **exclude China's absolute largest tier-1 megacities** (specifically Beijing, Shanghai, Guangzhou, Chongqing, and Tianjin).

By centering on dynamic provincial capitals (e.g., Chengdu, Wuhan, Xi'an, Zhengzhou), specialized manufacturing nodes (e.g., Shenzhen, Zhuhai, Taizhou, Zibo), ancient Silk Road oases (e.g., Kashgar, Hotan, Wuwei), and strategic border gateways (e.g., Dandong, Hunchun), this ratlas examines how physical urbanization and infrastructure modernization transformed the full depth of China's urban hierarchy beyond the global superstar metropolises.
:::

## 1. Population Ranking (2020 Census)

The master ranking across this project is ordered by **Permanent Resident Population (常住人口)** derived from the **Seventh National Population Census of the People's Republic of China (第七次全国人口普查 / 七普 2020)**:

- **Sub-provincial & Prefecture-Level Cities**: Measured by total permanent resident population across municipal jurisdictions.
- **County-Level Cities**: For specialized county-level cities in the sample (Hunchun, Korla, Hotan, Taishan), measured by the official resident population of the county-level city administrative unit.
- **Rank Range**: Spans from **#1 Chengdu (20.94 Million)** down to **#47 Hunchun (0.24 Million)**.

## 2. Satellite Urban Growth Engine: DLR WSF Evolution

The physical urban growth data in this project is driven by the **World Settlement Footprint Evolution (WSF Evolution)** dataset, produced by the **German Aerospace Center (DLR)**:

- **Spatial Resolution**: 30 meters per pixel, derived from joint multi-decadal analysis of **Landsat-5, Landsat-7, and Landsat-8** optical imagery, integrated with radar and digital elevation datasets.
- **Temporal Coverage**: 1985 to 2015 (30-year span).
- **Pixel Semantics**: Each pixel value encodes the exact calendar year ($1985 \le \text{year} \le 2015$) in which human settlement was first detected. Value `0` represents non-urban surfaces. Value `1985` represents human settlements already established by or prior to 1985.
- **Open Web Retrieval**: Retrieved directly from DLR's open data servers (`download.geoservice.dlr.de`) using GDAL virtual file streaming (`/vsicurl/`) and R's `terra` package.

## 3. High-Speed Rail (HSR) Network Integration

China's **High-Speed Rail (CRH / 中国高铁)** network—the defining infrastructure project of the 21st century—is mapped alongside the cities. Over the 2006–2015 era, high-speed rail catalyzed spatial expansion by connecting regional capitals and satellite towns:

- **Corridors Included**: The primary "Eight Vertical and Eight Horizontal" (*Ba Zong Ba Heng*) trunk corridors, including the Beijing–Hong Kong Corridor, Beijing–Shanghai Corridor, Eurasian Continental Bridge Corridor (Lanzhou–Xinjiang HSR), Yangtze River Corridor (Huhanrong), Shanghai–Kunming Corridor, Coastal Corridor, Xi'an–Chengdu HSR, and Hainan Island Ring HSR.
- **Spatial Traces**: Vector geometries compiled from OpenStreetMap railway relations and Natural Earth 10m transportation datasets.

## 4. Four Landmark Urban Development Epochs

Urban expansion in modern China has unfolded in distinct historical waves:

1. **Pre-1985 Core** (`#F59E0B` · Amber Gold):
   The pre-reform base urban footprint. This includes ancient historical city cores and the industrial settlements constructed during the early Five-Year Plans (1949–1980).
2. **1986–1995 Wave** (`#EF4444` · Crimson Coral):
   Deng Xiaoping's 1992 Southern Tour (*Nanxun*), the launch of Special Economic Zones (SEZs), and the initial surge of rural-to-urban industrialization.
3. **1996–2005 Wave** (`#06B6D4` · Electric Cyan):
   China's 2001 accession to the World Trade Organization (WTO), the emergence of the "Factory of the World", highway grid expansion, and initial high-tech development zones.
4. **2006–2015 Wave** (`#10B981` · Emerald Green):
   The High-Speed Rail (HSR) construction boom, the Western Development Strategy (*Xibu Da Kaifa*), massive State-level New Areas (*Guojiaji Xinqu*), and metropolitan amalgamation.

## 5. Quantitative Metrics

- **Cumulative Built-Up Area ($A_t$)**: Total surface area in $\text{km}^2$ occupied by detected settlements at year $t$.
- **Net Spatial Gain ($\Delta A$)**: $A_{2015} - A_{1985}$.
- **30-Year Growth Multiple ($M$)**: $A_{2015} / A_{1985}$.
- **Compound Annual Growth Rate (CAGR)**: $\left(\frac{A_{2015}}{A_{1985}}\right)^{1/30} - 1$.
"""
with open("methodology.qmd", "w", encoding="utf-8") as f:
    f.write(methodology_qmd.strip() + "\n")

# ------------------------------------------------------------------------------
# 5. Generate Home Page (index.qmd)
# ------------------------------------------------------------------------------
imagemap_html = """```{=html}
<div style="position: relative; width: 100%; max-width: 1100px; margin: 1.5rem auto; border-radius: 10px; overflow: hidden; border: 1px solid #1f2937; box-shadow: 0 10px 30px rgba(0,0,0,0.7);">
  <!-- Base Regional Map Graphic -->
  <img src="output/maps/china_regions_map.png" usemap="#chinaregions" alt="China Geographic Regions Map" style="width: 100%; height: auto; display: block;">

  <!-- Interactive SVG Clickable Overlay with Glowing Regions -->
  <svg viewBox="0 0 1600 1100" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: auto;">
    <style>
      .reg-link { cursor: pointer; transition: all 0.25s ease; }
      .reg-poly { fill: transparent; stroke: transparent; stroke-width: 3; transition: all 0.25s ease; }
      .reg-link:hover .reg-poly { fill: rgba(56, 189, 248, 0.28); stroke: #38bdf8; filter: drop-shadow(0 0 12px rgba(56, 189, 248, 0.9)); }
      .reg-link text { fill: #f8fafc; font-size: 26px; font-weight: bold; text-anchor: middle; pointer-events: none; opacity: 0.9; text-shadow: 0 2px 6px rgba(0,0,0,0.9); }
    </style>

    <!-- Northeast Rust Belt -->
    <a href="regions/northeast.html" class="reg-link" title="Northeast Rust Belt (8 Cities)">
      <polygon class="reg-poly" points="1160,80 1560,80 1560,420 1200,450 1160,350" />
      <text x="1350" y="240">Northeast Rust Belt →</text>
    </a>

    <!-- Yellow River & North Plain -->
    <a href="regions/northern_plains.html" class="reg-link" title="Yellow River & North Plain (11 Cities)">
      <polygon class="reg-poly" points="960,380 1260,380 1260,600 960,600" />
      <text x="1110" y="490">North Plain & Bohai →</text>
    </a>

    <!-- Yangtze Delta & East -->
    <a href="regions/yangtze_delta.html" class="reg-link" title="Yangtze Delta & East (5 Cities)">
      <polygon class="reg-poly" points="1090,560 1260,560 1260,730 1090,730" />
      <text x="1180" y="650">Yangtze Delta →</text>
    </a>

    <!-- Yangtze Basin & Central -->
    <a href="regions/yangtze_basin.html" class="reg-link" title="Yangtze Basin & Central (6 Cities)">
      <polygon class="reg-poly" points="760,590 1100,590 1100,780 760,780" />
      <text x="930" y="690">Yangtze Basin & Central →</text>
    </a>

    <!-- Pearl River & South Coast -->
    <a href="regions/coastal_south.html" class="reg-link" title="Pearl River & South Coast (6 Cities)">
      <polygon class="reg-poly" points="890,780 1230,780 1230,1020 890,1020" />
      <text x="1060" y="900">Pearl River & South Coast →</text>
    </a>

    <!-- Western Frontier & Steppe -->
    <a href="regions/western_frontier.html" class="reg-link" title="Western Frontier & Steppe (11 Cities)">
      <polygon class="reg-poly" points="50,180 960,180 820,950 50,700" />
      <text x="480" y="460">Western Frontier & Steppe →</text>
    </a>
  </svg>

  <!-- Standard HTML5 Image Map Fallback -->
  <map name="chinaregions">
    <area shape="poly" coords="1160,80,1560,80,1560,420,1200,450,1160,350" href="regions/northeast.html" alt="Northeast Rust Belt">
    <area shape="poly" coords="960,380,1260,380,1260,600,960,600" href="regions/northern_plains.html" alt="Yellow River & North Plain">
    <area shape="poly" coords="1090,560,1260,560,1260,730,1090,730" href="regions/yangtze_delta.html" alt="Yangtze Delta & East">
    <area shape="poly" coords="760,590,1100,590,1100,780,760,780" href="regions/yangtze_basin.html" alt="Yangtze Basin & Central">
    <area shape="poly" coords="890,780,1230,780,1230,1020,890,1020" href="regions/coastal_south.html" alt="Pearl River & South Coast">
    <area shape="poly" coords="50,180,960,180,820,950,50,700" href="regions/western_frontier.html" alt="Western Frontier & Steppe">
  </map>
</div>
```"""

index_hero = """```{=html}
<div class="hero-banner">
  <div style="max-width: 900px;">
    <h1 class="hero-title">China Urban Growth Ratlas</h1>
    <h2 style="color: #f59e0b; font-size: 1.5rem; margin-top: -0.25rem; margin-bottom: 1rem;">中国城市空间扩展图集 · 1985–2015</h2>
    <p class="hero-subtitle">
      Between 1985 and 2015, the People's Republic of China underwent the largest physical urbanization process in human history. 
      This ratlas maps the spatial morphology, expansion rings, High-Speed Rail corridors, and quantitative growth trajectories across <strong>47 diverse Chinese cities</strong> ranked by population.
    </p>
    <div style="display: flex; gap: 1rem; margin-top: 1.5rem; flex-wrap: wrap;">
      <a href="cities.html" class="btn btn-primary" style="background: #0284c7; border: none; padding: 0.6rem 1.25rem; font-weight: 600;">Browse All 47 Cities →</a>
      <a href="methodology.html" class="btn btn-secondary" style="background: #1e293b; color: #cbd5e1; border: 1px solid #334155; padding: 0.6rem 1.25rem;">Methodology & Data</a>
    </div>
  </div>
</div>
```"""

selection_callout = """::: {.callout-note appearance="simple" icon=true}
## Scope & Sample Selection: Excluding Tier-1 Superstar Megacities
The 47 cities in this atlas were deliberately selected to **exclude China's absolute largest tier-1 megacities** (specifically Beijing, Shanghai, Guangzhou, Chongqing, and Tianjin).

By centering on dynamic provincial capitals (e.g., Chengdu, Wuhan, Xi'an, Zhengzhou), specialized manufacturing nodes (e.g., Shenzhen, Zhuhai, Taizhou, Zibo), ancient Silk Road oases (e.g., Kashgar, Hotan, Wuwei), and strategic border gateways (e.g., Dandong, Hunchun), this ratlas examines how physical urbanization and infrastructure modernization transformed the full depth of China's urban hierarchy beyond the global superstar metropolises.
:::"""

index_qmd = f"""---
title: "China Urban Growth Ratlas (1985–2015)"
subtitle: "A Geospatial Exploration of 30 Years of Physical Expansion Across 47 Chinese Metropolises"
format:
  html:
    toc: true
---

{index_hero}

{selection_callout}

## Key Findings & National Overview

::: {{.metric-grid}}
::: {{.metric-card}}
::: {{.metric-label}}
Total Cities Analyzed
:::
::: {{.metric-val}}
47
:::
<div style="font-size: 0.8rem; color: #38bdf8;">Ranked by Population</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
Largest City (2020)
:::
::: {{.metric-val}}
20.9 <span style="font-size: 1rem;">M</span>
:::
<div style="font-size: 0.8rem; color: #f59e0b;">Chengdu (成都市)</div>
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
<div style="font-size: 0.8rem; color: #10b981;">Chengdu (成都市)</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
Transit Integration
:::
::: {{.metric-val}}
CRH
:::
<div style="font-size: 0.8rem; color: #38bdf8;">High-Speed Rail Grid</div>
:::
:::

---

## National Urban Expansion & High-Speed Rail Map

The map below displays all 47 cities in the ratlas across China, sized by **2020 Census Population**, colored by **30-year growth multiplier**, and overlaid with China's **High-Speed Rail network (CRH 高铁)**:

::: {{.map-container}}
!['China Urban Growth Ratlas National Overview & High-Speed Rail'](output/maps/china_overview_map.png)
:::

---

## High-Speed Rail Network & Urban Hierarchy

China's High-Speed Rail network physically stitched together regional capitals and secondary nodes, accelerating post-2005 outward expansion:

::: {{.map-container}}
!['China High-Speed Rail Network and Atlas Nodes'](output/maps/china_hsr_overview.png)
:::

---

## 30-Year Growth Multiplier Rankings

Which cities experienced the highest relative spatial expansion between 1985 and 2015?

::: {{.map-container}}
!['Top 25 Cities by 30-Year Urban Growth Multiple'](output/plots/national_growth_ranking.png)
:::

---

## Interactive Regional Explorations

Click any region on the interactive map below to jump directly to its dedicated regional chapter, or explore via the region cards below:

{imagemap_html}

::: {{.columns}}

::: {{.column width="32%"}}
::: {{.region-card}}
### [Pearl River & South Coast](regions/coastal_south.html)
Special Economic Zones, export engines, and coastal reclaimers.
- **Cities**: Shenzhen, Xiamen, Haikou, Heyuan, Zhuhai, Taishan
[Explore Region →](regions/coastal_south.html)
:::
:::

::: {{.column width="32%"}}
::: {{.region-card}}
### [Yangtze Basin & Central](regions/yangtze_basin.html)
Inland megacities and riverine industrial corridors.
- **Cities**: Chengdu, Wuhan, Nanchang, Luzhou, Yichang, Zhangjiajie
[Explore Region →](regions/yangtze_basin.html)
:::
:::

::: {{.column width="32%"}}
::: {{.region-card}}
### [Yangtze Delta & East](regions/yangtze_delta.html)
Interconnected manufacturing clusters and canal towns.
- **Cities**: Lianyungang, Yangzhou, Taizhou, Wuhu, Huangshan
[Explore Region →](regions/yangtze_delta.html)
:::
:::

:::

::: {{.columns}}

::: {{.column width="32%"}}
::: {{.region-card}}
### [Yellow River & North Plain](regions/northern_plains.html)
Heavy industrial centers across the agricultural heartland.
- **Cities**: Zhengzhou, Shijiazhuang, Baoding, Jinan, Jining, Liaocheng...
[Explore Region →](regions/northern_plains.html)
:::
:::

::: {{.column width="32%"}}
::: {{.region-card}}
### [Northeast Rust Belt](regions/northeast.html)
Early industrial powerhouses and international border gateways.
- **Cities**: Harbin, Tieling, Dandong, Fuxin, Baicheng, Panjin...
[Explore Region →](regions/northeast.html)
:::
:::

::: {{.column width="32%"}}
::: {{.region-card}}
### [Western Frontier & Steppe](regions/western_frontier.html)
Silk Road oasis towns, highland capitals, and desert gateways.
- **Cities**: Xi'an, Kunming, Guilin, Lanzhou, Urumqi, Hohhot, Kashgar...
[Explore Region →](regions/western_frontier.html)
:::
:::

:::

---

## Complete 47-City Master Index (Ranked by Population)

| Pop Rank | City | Chinese | Province | Region | Population (2020) | 1985 Area | 2015 Area | Net Gain | Multiplier | CAGR |
|:---:|:---|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
{all_rows}

---

::: {{.caption-box}}
**China Urban Growth Ratlas** · Built with R (`terra`, `sf`, `ggplot2`, `tidyterra`, `patchwork`) and Quarto. Data: German Aerospace Center (DLR) World Settlement Footprint Evolution (30m), 7th National Population Census (七普 2020), OpenStreetMap CRH High-Speed Rail Grid & GADM 4.1.
:::
"""

with open("index.qmd", "w", encoding="utf-8") as f:
    f.write(index_qmd.strip() + "\n")

print("Generated all Quarto source documents successfully with {=html} blocks!")
