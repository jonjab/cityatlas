import json, os

with open("data/processed/city_growth_stats.json", "r", encoding="utf-8") as f:
    cities = json.load(f)

with open("data/processed/city_rail_summary.json", "r", encoding="utf-8") as f:
    rail_summaries = json.load(f)

with open("data/processed/city_wiki_resources.json", "r", encoding="utf-8") as f:
    wiki_resources = json.load(f)

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
# 1. Generate Individual City Pages (Using raw {=html} blocks + Complete Citations)
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

    arc_rank_text = f"#{c.get('arcgis_rank', 'N/A')}" if c.get('arcgis_rank') else "N/A"
    rail_info = rail_summaries.get(c_id, {
        "total_rail_segments": 0,
        "hsr_segments": 0,
        "conventional_segments": 0,
        "station_count": 0,
        "major_corridors": [],
        "key_stations": []
    })
    wiki_res = wiki_resources.get(c_id, {})

    wiki_en_url = wiki_res.get("wikipedia_en_url", f"https://en.wikipedia.org/wiki/{c['name_en']}")
    wiki_zh_url = wiki_res.get("wikipedia_zh_url", f"https://zh.wikipedia.org/wiki/{c['name_zh']}")
    wikidata_id = wiki_res.get("wikidata_id", "Q")
    wikidata_url = wiki_res.get("wikidata_url", "https://www.wikidata.org")
    commons_cat_url = wiki_res.get("commons_map_category_url", f"https://commons.wikimedia.org/wiki/Category:Maps_of_{c['name_en']}")
    commons_search_url = wiki_res.get("commons_search_maps_url", f"https://commons.wikimedia.org/w/index.php?search={c['name_en']}+map")

    hero_block = f"""```{{=html}}
<div class="hero-banner">
  <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
    <div>
      <h1 style="color: #ffffff; margin-bottom: 0.25rem;">{c['name_en']} <span style="color: #f59e0b; font-weight: normal;">{c['name_zh']}</span></h1>
      <p style="color: #94a3b8; font-size: 1.1rem; margin: 0;">{c['pinyin']} · {c['province_en']} ({c['province_zh']}) · {c['region']}</p>
      <p style="color: #cbd5e1; font-size: 0.95rem; margin-top: 0.35rem;">
        Population: <strong>{c['pop_million']} Million</strong> (2020 Census) · 
        Population Rank: <strong>#{c['rank_population']}</strong> of 47 · 
        ArcGIS Urban Hierarchy Rank: <strong>{arc_rank_text}</strong>
      </p>
      <div style="margin-top: 0.75rem; display: flex; flex-wrap: wrap; gap: 0.5rem;">
        <a href="{wiki_en_url}" target="_blank" rel="noopener" class="resource-btn">📖 Wikipedia (EN)</a>
        <a href="{wiki_zh_url}" target="_blank" rel="noopener" class="resource-btn">🌐 维基百科 (ZH)</a>
        <a href="{wikidata_url}" target="_blank" rel="noopener" class="resource-btn">🏷️ Wikidata ({wikidata_id})</a>
        <a href="{commons_cat_url}" target="_blank" rel="noopener" class="resource-btn">🗺️ Commons Maps</a>
        <a href="{commons_search_url}" target="_blank" rel="noopener" class="resource-btn">🔍 Scanned Maps</a>
      </div>
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

    # Format railway details
    corridors_md = ""
    if rail_info.get("major_corridors"):
        corridor_pills = ", ".join(f"`{x}`" for x in rail_info["major_corridors"][:10])
        corridors_md = f"- **Major Railway Lines & Corridors**: {corridor_pills}\n"

    stations_md = ""
    if rail_info.get("key_stations"):
        station_pills = ", ".join(f"`{x}`" for x in rail_info["key_stations"][:10])
        stations_md = f"- **Major Passenger Terminals & Stations**: {station_pills}\n"

    # Format scanned maps callout
    old_map_line = ""
    if wiki_res.get("commons_old_map_category_url"):
        old_map_line = f"- 📜 **Historical Maps Collection**: [{wiki_res['commons_old_map_category']}]({wiki_res['commons_old_map_category_url']}) — Scanned historical maps, municipal plans, and early surveys.\n"

    scanned_maps_list = ""
    if wiki_res.get("scanned_maps"):
        scanned_items = []
        for sm in wiki_res["scanned_maps"]:
            scanned_items.append(f"- [{sm['title']}]({sm['url']}) (Wikimedia Commons scanned asset)")
        scanned_maps_list = "\n".join(scanned_items)
        scanned_maps_box = f"""::: {{.callout-note title="Selected Scanned Historical Maps on Wikimedia Commons"}}
The following scanned historical maps and cartographic surveys covering **{c['name_en']}** are accessible on Wikimedia Commons:

{scanned_maps_list}

Additional scanned historical maps and topographic sheets can be found via the [Wikimedia Commons Scanned Maps Search]({commons_search_url}).
:::"""
    else:
        scanned_maps_box = f"""::: {{.callout-note title="Scanned Historical Maps Archive"}}
Explore scanned historical maps, AMS sheets, and municipal surveys for **{c['name_en']}** directly on the [Wikimedia Commons Scanned Maps Search]({commons_search_url}).
:::"""

    qmd_content = f"""---
title: "{c['name_en']} ({c['name_zh']})"
subtitle: "Population: {c['pop_million']}M · 30-Year Growth: {c['growth_multiple']}× · {c['province_en']}"
format:
  html:
    toc: true
---

{hero_block}

## Key Urban Expansion & Hierarchy Indicators

::: {{.metric-grid}}
::: {{.metric-card}}
::: {{.metric-label}}
2020 Population
:::
::: {{.metric-val}}
{c['pop_million']} <span style="font-size: 1rem; color: #94a3b8;">M</span>
:::
<div style="font-size: 0.8rem; color: #38bdf8;">Pop Rank #{c['rank_population']} of 47</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
ArcGIS City Rank
:::
::: {{.metric-val}}
{arc_rank_text}
:::
<div style="font-size: 0.8rem; color: #94a3b8;">National Big Cities Tier</div>
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
<div style="font-size: 0.8rem; color: #f59e0b;">Multiplier Rank #{c['rank_multiplier']}</div>
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

The cartographic poster below maps the physical settlement rings of **{c['name_en']}** across four historical development epochs, overlaid with the high-precision HOTOSM / OpenStreetMap railway transit network:

- <span style="color: #F59E0B; font-weight: bold;">● Pre-1985 Core</span>: Historic urban core and initial post-1949 industrial settlements.
- <span style="color: #EF4444; font-weight: bold;">● 1986–1995 Wave</span>: Early reform, opening up, and Deng Xiaoping's 1992 Southern Tour (*Nanxun*).
- <span style="color: #06B6D4; font-weight: bold;">● 1996–2005 Wave</span>: WTO entry, export industrialization, and new development zones (*Kaifaqu*).
- <span style="color: #10B981; font-weight: bold;">● 2006–2015 Wave</span>: High-speed rail expansion, modern new cities (*Xinqu*), and peri-urban consolidation.
- <span style="color: #38BDF8; font-weight: bold;">━ Railway Corridors</span>: High-precision vector railway network overlaid directly from HOTOSM / OpenStreetMap (high-speed passenger corridors in vibrant cyan, conventional rail lines in silver).

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

## 3. Detailed Rail Network & Transit Corridors

The high-resolution vector map below provides a detailed visualization of the railway network across **{c['name_en']}**, extracted from OpenStreetMap and the Humanitarian OpenStreetMap Team (HOTOSM). The transit network is superimposed directly over the 2015 built settlement footprint (dark slate silhouette):

::: {{.map-container}}
!['Transit & Rail Network: {c['name_en']}'](../output/maps/{c_id}_rail.png)
:::

### Transit Infrastructure Indicators

::: {{.metric-grid}}
::: {{.metric-card}}
::: {{.metric-label}}
Total Track Segments
:::
::: {{.metric-val}}
{rail_info['total_rail_segments']:,}
:::
<div style="font-size: 0.8rem; color: #38bdf8;">HOTOSM Vector Lines</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
High-Speed Rail Segments
:::
::: {{.metric-val}}
{rail_info['hsr_segments']:,}
:::
<div style="font-size: 0.8rem; color: #38bdf8;">PDL / 250–350 km/h</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
Conventional Rail
:::
::: {{.metric-val}}
{rail_info['conventional_segments']:,}
:::
<div style="font-size: 0.8rem; color: #94a3b8;">Trunk & Connector Lines</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
Stations & Terminals
:::
::: {{.metric-val}}
{rail_info['station_count']:,}
:::
<div style="font-size: 0.8rem; color: #f59e0b;">Passenger Hubs</div>
:::
:::

{corridors_md}
{stations_md}

> **Transit Layer Citation**: Humanitarian OpenStreetMap Team (HOTOSM) & United Nations Office for the Coordination of Humanitarian Affairs (UN OCHA) Centre for Humanitarian Data, *Railways of China Dataset* on HDX ([https://data.humdata.org/dataset/hotosm_chn_railways](https://data.humdata.org/dataset/hotosm_chn_railways)). Feature geometries extracted from OpenStreetMap under the [Open Database License (ODbL 1.0)](https://opendatacommons.org/licenses/odbl/1-0/) by OpenStreetMap contributors. Includes passenger-dedicated high-speed lines, electrified conventional trunk corridors, industrial spurs, and passenger stations.

---

## 4. Geographical Location & Growth Trajectory

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

## 5. 5-Year Milestone Chronology

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

## 6. Archival Cartography & Wiki Resources

Direct links to open knowledge, semantic geodata, and scanned map collections for **{c['name_en']}**:

- 📖 **English Wikipedia**: [{wiki_res.get('wikipedia_en_title', c['name_en'])}]({wiki_en_url}) — In-depth overview of history, urban development, demographic shifts, and regional governance.
- 🌐 **Chinese Wikipedia (中文维基百科)**: [{wiki_res.get('wikipedia_zh_title', c['name_zh'])}]({wiki_zh_url}) — Authoritative municipal boundaries, administrative subdivisions, and local transport infrastructure.
- 🏷️ **Wikidata Knowledge Base**: [{wikidata_id} ({c['name_en']})]({wikidata_url}) — Semantic knowledge graph entity with geocoordinates, OpenStreetMap tags, and linked administrative entities.
- 🗺️ **Wikimedia Commons Map Repository**: [{wiki_res.get('commons_map_category', 'Maps of ' + c['name_en'])}]({commons_cat_url}) — Community-curated media repository containing thematic, administrative, and transport maps.
{old_map_line}- 🔍 **Scanned Maps & Historical Sheets Search**: [Explore scanned bitmap and topographic maps of {c['name_en']} on Wikimedia Commons]({commons_search_url})

{scanned_maps_box}

---

## 7. Data Sources & Attributions

The quantitative and spatial indicators for **{c['name_en']}** are synthesized from the following primary sources:

1. **Urban Footprint & Built-Up Surface**: German Aerospace Center (DLR) [World Settlement Footprint Evolution (1985–2015)](https://download.geoservice.dlr.de/WSF_EVO/). 30m resolution multi-decadal satellite detection (*Marconcini et al., 2020, Nature Scientific Data*).
2. **Permanent Resident Population**: National Bureau of Statistics of China (NBS), [Seventh National Population Census (第七次全国人口普查 / 七普 2020)](http://www.stats.gov.cn/). Resident population: **{c['pop_million']}M** (National Rank: **#{c['rank_population']}** of 47).
3. **National Urban Tier Classification**: Esri / [ArcGIS Online Big Cities Points FeatureServer](https://services1.arcgis.com/4TXrdeWh0RyCqPgB/arcgis/rest/services/big_cities_points/FeatureServer), National City Rank: **{arc_rank_text}** of 184 major Chinese cities.
4. **Detailed Transit & Railway Corridors**: Humanitarian OpenStreetMap Team (HOTOSM) & UN OCHA, [Railways of China Dataset](https://data.humdata.org/dataset/hotosm_chn_railways) on HDX. Licensed under the [Open Database License (ODbL 1.0)](https://opendatacommons.org/licenses/odbl/1-0/) by OpenStreetMap contributors. Includes full-precision railway alignments, high-speed rail lines, electrified conventional routes, and station points.
5. **Administrative Boundaries**: [GADM Database of Global Administrative Areas (v4.1)](https://gadm.org/), University of California, Davis.
6. **Archival Cartography & Encyclopedia Resources**: [Wikimedia Foundation](https://www.wikimedia.org/) ([Wikipedia](https://en.wikipedia.org/), [Wikidata](https://www.wikidata.org/), and [Wikimedia Commons](https://commons.wikimedia.org/)).

---

{footer_nav}
"""
    with open(f"cities/{c_id}.qmd", "w", encoding="utf-8") as f:
        f.write(qmd_content.strip() + "\n")

print(f"Generated 47 individual city QMD documents in cities/ with structured source citations.")

# ------------------------------------------------------------------------------
# 2. Generate Regional Pages (Sorted by Population + Regional Citations)
# ------------------------------------------------------------------------------
for rk, rv in regions_map.items():
    r_cities = sorted(rv["cities"], key=lambda x: x["rank_population"])
    
    rows = ""
    city_links = ""
    for c in r_cities:
        arc_rank_cell = f"#{c.get('arcgis_rank')}" if c.get('arcgis_rank') else "-"
        rows += f"""| #{c['rank_population']} | [{c['name_en']}](../cities/{c['id']}.html) | {c['name_zh']} | {c['province_en']} | **{c['pop_million']}M** | {arc_rank_cell} | {c['area_1985']} km² | {c['area_2015']} km² | +{c['net_gain_km2']} km² | **{c['growth_multiple']}×** | {c['cagr_pct']}% |\n"""
        
        city_links += f"""
::: {{.region-card}}
### [{c['name_en']} ({c['name_zh']})](../cities/{c['id']}.html)
**{c['province_en']} Province** · Population: <strong style="color: #38bdf8;">{c['pop_million']} Million</strong> (Rank #{c['rank_population']}) · ArcGIS Hierarchy Rank: <strong>{arc_rank_cell}</strong> · 30-Year Multiplier: <strong style="color: #f59e0b;">{c['growth_multiple']}×</strong>

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

| Pop Rank | City | Chinese | Province | Population | ArcGIS Rank | 1985 Area | 2015 Area | Net Gain | Multiplier | CAGR |
|:---:|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
{rows}

---

## Member City Profiles

{city_links}

---

## Data Sources & Regional Attributions

Data presented in this regional overview is derived from:
- **DLR WSF Evolution (1985–2015)**: German Aerospace Center (30m settlement detection).
- **Seventh National Population Census (2020)**: National Bureau of Statistics of China (NBS).
- **ArcGIS Online Big Cities Points**: Esri / public feature service `big_cities_points`.
- **HOTOSM Railways of China**: Humanitarian OpenStreetMap Team via Humanitarian Data Exchange (HDX).
- **GADM Administrative Areas (v4.1)**: UC Davis.
"""
    with open(f"regions/{rk}.qmd", "w", encoding="utf-8") as f:
        f.write(reg_content.strip() + "\n")

print("Generated 6 regional QMD documents in regions/.")

# ------------------------------------------------------------------------------
# 3. Generate All Cities Directory (cities.qmd)
# ------------------------------------------------------------------------------
all_rows = ""
for c in cities:
    arc_rank_cell = f"#{c.get('arcgis_rank')}" if c.get('arcgis_rank') else "-"
    all_rows += f"""| #{c['rank_population']} | [{c['name_en']}](cities/{c['id']}.html) | {c['name_zh']} | {c['province_en']} | {c['region']} | **{c['pop_million']}M** | {arc_rank_cell} | {c['area_1985']} km² | {c['area_2015']} km² | +{c['net_gain_km2']} km² | **{c['growth_multiple']}×** | {c['cagr_pct']}% |\n"""

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
  <p style="color: #cbd5e1; margin: 0;">Complete inventory of all 47 cities analyzed in this project, ranked from largest to smallest population based on the 7th National Population Census (七普 2020) and cross-referenced with ArcGIS Online Big Cities Points.</p>
</div>
```

::: {{.callout-note appearance="simple"}}
**Selection Note**: Cities were selected to exclude China's tier-1 superstar megacities (Beijing, Shanghai, Guangzhou, Chongqing, Tianjin) to examine dynamic provincial capitals, regional economic drivers, and specialized border gateways.
:::

| Pop Rank | City | Chinese | Province | Region | Population | ArcGIS Rank | 1985 Area | 2015 Area | Net Gain | Multiplier | CAGR |
|:---:|:---|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
{all_rows}

---

::: {{.caption-box}}
**Data Sources**: DLR World Settlement Footprint Evolution 30m (Marconcini et al., 2020) · 7th National Population Census of China (2020) · ArcGIS Online Big Cities Points · HOTOSM Railways of China (HDX) · GADM 4.1.
:::
"""
with open("cities.qmd", "w", encoding="utf-8") as f:
    f.write(cities_qmd.strip() + "\n")

# ------------------------------------------------------------------------------
# 4. Generate Comprehensive Academic Methodology Page (methodology.qmd)
# ------------------------------------------------------------------------------
methodology_qmd = r"""---
title: "Data & Methodology"
subtitle: "Comprehensive Data Sources, Academic Citations, Processing Pipelines, and Analytical Framework"
format:
  html:
    toc: true
---

```{=html}
<div class="hero-banner">
  <h1 style="color: #ffffff; margin-bottom: 0.5rem;">Analytical Methodology & Citations</h1>
  <p style="color: #cbd5e1; margin: 0;">Comprehensive documentation of data sources, academic citations, licensing terms, spatial processing workflows, and mathematical formulas underpinning the China Urban Growth Ratlas.</p>
</div>
```

::: {.callout-important appearance="simple"}
## Scope & Sample Selection Note: Excluding Tier-1 Megacities
The 47 cities in this atlas were deliberately selected to **exclude China's absolute largest tier-1 megacities** (specifically Beijing, Shanghai, Guangzhou, Chongqing, and Tianjin).

By centering on dynamic provincial capitals (e.g., Chengdu, Wuhan, Xi'an, Zhengzhou), specialized manufacturing nodes (e.g., Shenzhen, Zhuhai, Taizhou, Zibo), ancient Silk Road oases (e.g., Kashgar, Hotan, Wuwei), and strategic border gateways (e.g., Dandong, Hunchun), this ratlas examines how physical urbanization and infrastructure modernization transformed the full depth of China's urban hierarchy beyond the global superstar metropolises.
:::

## 1. Primary Data Sources & Scholarly References

### A. DLR World Settlement Footprint Evolution (WSF Evolution)
- **Data Custodian**: German Aerospace Center (Deutsches Zentrum für Luft- und Raumfahrt; DLR), Earth Observation Center (EOC).
- **Spatial Resolution**: 30 meters per pixel, global coverage.
- **Sensor Inputs**: Multi-decadal archive of joint optical (Landsat-5 TM, Landsat-7 ETM+, Landsat-8 OLI) and radar (ERS-1/2, Sentinel-1) satellite observations.
- **Pixel Encoding**: Integer values between `1985` and `2015` represent the exact year of earliest detected settlement establishment. Value `0` denotes unbuilt natural/agricultural surfaces.
- **Data Access**: Retrieved via HTTP range requests through GDAL virtual filesystem (`/vsicurl/`) from `https://download.geoservice.dlr.de/WSF_EVO/`.
- **Primary Scholarly Citation**:
  > Marconcini, M., Metz, A., Üreyen, S., Palacios-Lopez, D., Hanke, W., Bachofer, F., Zeidler, J., Esch, T., Gorelick, N., Kakarla, A., Paganini, M., & Strano, E. (2020). *Outlining where humans live, the World Settlement Footprint 2015.* **Scientific Data**, 7(1), 242. [https://doi.org/10.1038/s41597-020-00580-5](https://doi.org/10.1038/s41597-020-00580-5)
- **Evolution Methodology Citation**:
  > Marconcini, M., Metz, A., Zeidler, J., & Esch, T. (2021). *The World Settlement Footprint Evolution—30 Years of Growth.* **Remote Sensing of Environment**, 255, 112282.

### B. HOTOSM Railways of China Dataset
- **Data Custodian**: Humanitarian OpenStreetMap Team (HOTOSM) & United Nations Office for the Coordination of Humanitarian Affairs (UN OCHA) Centre for Humanitarian Data.
- **Platform**: Humanitarian Data Exchange (HDX).
- **Data URL**: [https://data.humdata.org/dataset/hotosm_chn_railways](https://data.humdata.org/dataset/hotosm_chn_railways)
- **Content**: 433,889 vector railway features (415,414 track segments and 18,475 passenger stations) extracted from OpenStreetMap, categorized into passenger-dedicated lines (*PDL / 高铁*), intercity railways, standard gauge electrified lines, and station coordinates.
- **Processing**: Ingested in Python and R via `sf`; aggregated at the national level into 194 primary High-Speed Rail corridors (`data/processed/hotosm_hsr_lines.rds`), and spatially indexed into per-city railway vectors (`data/processed/city_rails.rds` and `data/processed/city_rail_summary.json`) driving both the hero growth rings overlay and dedicated transit maps (`{c_id}_rail.png`).
- **Citation & License**:
  > Humanitarian OpenStreetMap Team (HOTOSM). (2024). *Railways of China [Data set]*. Humanitarian Data Exchange (HDX). Licensed under the **Open Database License (ODbL 1.0)** by OpenStreetMap contributors.

### C. ArcGIS Online Big Cities Points Layer
- **Data Custodian**: Esri / ArcGIS Online Feature Services.
- **Service Endpoint**: [https://services1.arcgis.com/4TXrdeWh0RyCqPgB/arcgis/rest/services/big_cities_points/FeatureServer](https://services1.arcgis.com/4TXrdeWh0RyCqPgB/arcgis/rest/services/big_cities_points/FeatureServer)
- **Content**: Authoritative geospatial point layer of 184 major Chinese metropolitan centers with national hierarchy ranks (`rank` 1 to 200).
- **Role in Ratlas**: Validates sample selection, confirms exclusion of tier-1 megacities (#1 Shanghai, #2 Beijing, #3 Guangzhou, #5 Chongqing, #7 Tianjin), and provides an objective national urban hierarchy classification for every city in the atlas.
- **Citation**:
  > Esri ArcGIS Online. (2023). *Big Cities Points Layer [Feature Service]*. ArcGIS REST API.

### D. Seventh National Population Census of China (七普 2020)
- **Data Custodian**: National Bureau of Statistics of China (中华人民共和国国家统计局; NBS), Beijing, China.
- **Measurement**: Permanent Resident Population (*常住人口, Changzhu Renkou*) as of midnight, November 1, 2020.
- **Role in Ratlas**: Defines the primary sorting and ranking order across the entire ratlas from #1 Chengdu (20.94 Million) to #47 Hunchun (0.24 Million).
- **Official Citation**:
  > Office of the Leading Group of the State Council for the Seventh National Population Census. (2021). *Major Figures on 2020 Population Census of China.* China Statistics Press, Beijing. [http://www.stats.gov.cn/](http://www.stats.gov.cn/)

### E. GADM Database of Global Administrative Areas
- **Data Custodian**: University of California, Davis (UCD), Department of Environmental Science and Policy.
- **Version**: GADM 4.1 (released 2022).
- **Data URL**: [https://gadm.org/](https://gadm.org/)
- **Content**: Spatial administrative boundaries at Level 0 (national border), Level 1 (provinces), and Level 2 (prefectures and municipalities) with official bilingual toponyms.
- **Citation**:
  > Hijmans, R. J., Garcia, N., & Wieczorek, J. (2022). *GADM Database of Global Administrative Areas, Version 4.1*. University of California, Davis. [https://gadm.org/](https://gadm.org/)

### F. Wikimedia Foundation Open Knowledge & Cartographic Archives
- **Data Custodians**: Wikimedia Foundation, OpenStreetMap community, and participating international map libraries (including the Perry-Castañeda Library Map Collection, University of Texas at Austin).
- **Platforms**: [English Wikipedia](https://en.wikipedia.org/), [Chinese Wikipedia (中文维基百科)](https://zh.wikipedia.org/), [Wikidata](https://www.wikidata.org/), and [Wikimedia Commons](https://commons.wikimedia.org/).
- **Content & Integration**:
  - Direct encyclopedic references for every city linking demographic, historical, and urban policy context.
  - Persistent semantic Wikidata entities (`QID`) providing machine-readable administrative linkages.
  - Community-curated map categories (`Category:Maps of <City>` and `Category:Old maps of <City>`).
  - Scanned historical cartography, imperial treaty port surveys, early Republican plans, and US Army Map Service (AMS) 1:250,000 / 1:50,000 topographic map series.
- **Licenses**: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0), Creative Commons CC0 1.0 Public Domain Dedication, and Public Domain worldwide.

---

## 2. Data Licensing & Terms of Use

| Dataset | Provider | License / Terms of Use | Attribution Notice |
|:---|:---|:---|:---|
| **WSF Evolution** | German Aerospace Center (DLR) | Creative Commons Attribution 4.0 International (CC-BY 4.0) | © DLR (2020, 2021) |
| **Railways of China** | HOTOSM / OpenStreetMap | Open Data Commons Open Database License (ODbL 1.0) | © OpenStreetMap contributors, HOTOSM |
| **Big Cities Points** | Esri / ArcGIS Online | Esri Public REST Feature Service Terms | © Esri, ArcGIS Online Content Providers |
| **National Census (2020)** | National Bureau of Statistics (NBS) | Public Statistical Release / Government Open Data | Source: National Bureau of Statistics of China |
| **GADM Boundaries** | University of California, Davis | Free for non-commercial and academic use | © GADM (v4.1) |
| **Wiki Resources & Scanned Maps** | Wikimedia Foundation / Contributors | CC BY-SA 4.0 / CC0 / Public Domain | © Wikimedia contributors |

---

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

---

## 4. Quantitative Metrics & Mathematical Definitions

- **Cumulative Built-Up Area ($A_t$)**: Total surface area in square kilometers occupied by detected settlement pixels up to year $t$:
  $$A_t = \sum_{i \in \text{city}} a_i \cdot \mathbb{I}(1985 \le Y_i \le t)$$
  where $a_i$ is the ellipsoidal cell surface area computed via `terra::cellSize(unit = "km")`, and $Y_i$ is the year of first settlement detection at pixel $i$.
- **Net Spatial Expansion ($\Delta A$)**: Absolute urban land footprint expansion between 1985 and 2015:
  $$\Delta A = A_{2015} - A_{1985} \quad (\text{km}^2)$$
- **30-Year Growth Multiple ($M$)**: Relative spatial expansion factor:
  $$M = \frac{A_{2015}}{A_{1985}}$$
- **Compound Annual Growth Rate (CAGR)**: Annualized physical expansion rate over the 30-year observation window:
  $$\text{CAGR} = \left(\frac{A_{2015}}{A_{1985}}\right)^{1/30} - 1$$

---

## 5. Software Stack & Open Source Packages

- **R Environment**: R Core Team (2026). *R: A Language and Environment for Statistical Computing* (v4.6.1), R Foundation for Statistical Computing, Vienna, Austria.
- **Raster Processing**: Hijmans, R. J. (2024). `terra`: *Spatial Data Analysis*. R package version 1.9.50.
- **Vector Processing**: Pebesma, E. (2018). *Simple Features for R: Standardized Support for Spatial Vector Data*. **The R Journal**, 10(1), 439-446.
- **Cartographic Rendering**: Wickham, H. (2016). *ggplot2: Elegant Graphics for Data Analysis*. Springer-Verlag New York.
- **Raster Cartography**: Hernangómez, D. (2023). *Using the tidyverse with terra Objects: the tidyterra Package*. **Journal of Open Source Software**, 8(91), 5751.
- **Multi-Panel Layouts**: Pedersen, T. L. (2024). `patchwork`: *The Composer of Plots*. R package version 1.3.0.
- **Typography & Font Shaping**: `ragg` and `systemfonts` utilizing `Droid Sans Fallback` (Google Android Open Source Project) for CJK vector typography.
- **Publishing System**: Allaire, J. J., et al. (2024). *Quarto: An open-source scientific and technical publishing system*. Posit Software.
"""
with open("methodology.qmd", "w", encoding="utf-8") as f:
    f.write(methodology_qmd.strip() + "\n")

# ------------------------------------------------------------------------------
# 5. Generate Home Page (index.qmd + Comprehensive Attributions Table)
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
      This ratlas maps the spatial morphology, expansion rings, HOTOSM railway networks, and quantitative growth trajectories across <strong>47 diverse Chinese cities</strong> ranked by population.
    </p>
    <div style="display: flex; gap: 1rem; margin-top: 1.5rem; flex-wrap: wrap;">
      <a href="cities.html" class="btn btn-primary" style="background: #0284c7; border: none; padding: 0.6rem 1.25rem; font-weight: 600;">Browse All 47 Cities →</a>
      <a href="methodology.html" class="btn btn-secondary" style="background: #1e293b; color: #cbd5e1; border: 1px solid #334155; padding: 0.6rem 1.25rem;">Methodology & Citations</a>
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
HOTOSM
:::
<div style="font-size: 0.8rem; color: #38bdf8;">194 HSR Corridors</div>
:::
:::

---

## National Urban Expansion & HOTOSM Railways Map

The map below displays all 47 cities in the ratlas across China, sized by **2020 Census Population**, colored by **30-year growth multiplier**, overlaid with the **HOTOSM China Railways dataset (HDX)** and contextualized with **ArcGIS Online Big Cities Points**:

::: {{.map-container}}
!['China Urban Growth Ratlas National Overview & HOTOSM Railways'](output/maps/china_overview_map.png)
:::

---

## HOTOSM High-Speed Rail Network & Urban Hierarchy

China's High-Speed Rail grid physically stitched together regional capitals and secondary nodes, accelerating post-2005 outward expansion across the 184 major urban centers identified in the ArcGIS Online Big Cities layer:

::: {{.map-container}}
!['HOTOSM China High-Speed Rail Network and Urban Hierarchy'](output/maps/china_hsr_overview.png)
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

| Pop Rank | City | Chinese | Province | Region | Population (2020) | ArcGIS Rank | 1985 Area | 2015 Area | Net Gain | Multiplier | CAGR |
|:---:|:---|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
{all_rows}

---

## Primary Data Sources & Citations

This atlas synthesizes five open geospatial and authoritative statistical datasets. Detailed academic citations, licensing terms, and analytical documentation are available in the [Methodology & Citations](methodology.html) chapter.

| Dataset / Source | Custodian / Provider | Resolution / Coverage | Analytical Role in Ratlas | Primary Citation / Access |
|:---|:---|:---|:---|:---|
| **World Settlement Footprint Evolution (WSF Evolution)** | German Aerospace Center (DLR) | 30m / 1985–2015 Annual | Primary spatial engine; identifies exact year of settlement detection | [DLR Geoservice](https://download.geoservice.dlr.de/WSF_EVO/) · Marconcini et al. (2020, *Sci. Data*) |
| **Railways of China Dataset** | Humanitarian OpenStreetMap Team & UN OCHA | Vector / National | 194 High-Speed Rail corridors and transit infrastructure | [HDX HOTOSM Dataset](https://data.humdata.org/dataset/hotosm_chn_railways) · © OpenStreetMap contributors (ODbL) |
| **Big Cities Points Layer** | Esri / ArcGIS Online | Vector Points / 184 Cities | National city hierarchy ranking (1–200) and tier-1 anchor points | [ArcGIS FeatureServer](https://services1.arcgis.com/4TXrdeWh0RyCqPgB/arcgis/rest/services/big_cities_points/FeatureServer) |
| **Seventh National Population Census (七普 2020)** | National Bureau of Statistics of China (NBS) | Prefectural / 2020 | Primary ranking order (#1–#47) by permanent resident population | [NBS China Census Bulletin (2021)](http://www.stats.gov.cn/) |
| **GADM Administrative Areas (v4.1)** | University of California, Davis (UCD) | Levels 0, 1, 2 / National | Administrative boundary clipping and bilingual toponymy | [GADM v4.1](https://gadm.org/) · Hijmans et al. (2022) |

---

::: {{.caption-box}}
**China Urban Growth Ratlas** · Built with R (`terra`, `sf`, `ggplot2`, `tidyterra`, `patchwork`) and Quarto. Data: German Aerospace Center (DLR) World Settlement Footprint Evolution (30m), 7th National Population Census (七普 2020), HOTOSM Railways of China (HDX), ArcGIS Online Big Cities Points & GADM 4.1.
:::
"""

with open("index.qmd", "w", encoding="utf-8") as f:
    f.write(index_qmd.strip() + "\n")

print("Generated all Quarto source documents successfully with comprehensive source citations!")
