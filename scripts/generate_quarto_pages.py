import json, os

with open("data/processed/city_growth_stats.json", "r", encoding="utf-8") as f:
    cities = json.load(f)

comp_cities = []
if os.path.exists("data/processed/comparison_growth_stats.json"):
    with open("data/processed/comparison_growth_stats.json", "r", encoding="utf-8") as f:
        comp_cities = json.load(f)

with open("data/processed/city_rail_summary.json", "r", encoding="utf-8") as f:
    rail_summaries = json.load(f)

with open("data/processed/city_wiki_resources.json", "r", encoding="utf-8") as f:
    wiki_resources = json.load(f)

# Sort strictly by population rank (#1 to #47)
cities = sorted(cities, key=lambda x: x["rank_population"])

print(f"Loaded {len(cities)} Chinese cities ordered by population rank, and {len(comp_cities)} US comparison cities.")

# Regional mapping for China
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
# 1. Generate Individual Chinese City Pages
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
        "key_stations": [],
        "has_subway": False,
        "subway_lines_count": 0,
        "subway_station_count": 0,
        "subway_line_names": []
    })
    has_sub = rail_info.get("has_subway", False)
    subway_badge = f'<span class="metric-badge badge-blue" style="font-size: 0.85rem; margin-left: 0.5rem;">🚇 {rail_info.get("subway_lines_count")} Metro Lines</span>' if has_sub else ''
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
      <h1 style="color: #ffffff; margin-bottom: 0.25rem;">{c['name_en']} <span style="color: #f59e0b; font-weight: normal;">{c['name_zh']}</span> {subway_badge}</h1>
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

    corridors_md = ""
    if rail_info.get("major_corridors"):
        corridor_pills = ", ".join(f"`{x}`" for x in rail_info["major_corridors"][:10])
        corridors_md = f"- **Major Railway Lines & Corridors**: {corridor_pills}\n"

    stations_md = ""
    if rail_info.get("key_stations"):
        station_pills = ", ".join(f"`{x}`" for x in rail_info["key_stations"][:10])
        stations_md = f"- **Major Passenger Terminals & Stations**: {station_pills}\n"

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

    subway_narrative_block = ""
    if has_sub:
        lines_preview = ", ".join(f"`{x}`" for x in rail_info["subway_line_names"][:8])
        subway_narrative_block = f"""
::: {{.callout-tip title="Rapid Transit & Municipal Metro Infrastructure"}}
**{c['name_en']}** operates an extensive urban rapid transit network comprising **{rail_info['subway_lines_count']} operational metro lines** and **{rail_info['subway_station_count']} passenger stations** (source: AMap 高德地图 / Ministry of Transport of the PRC):

- **Key Metro Corridors**: {lines_preview}
- **Cartographic Overlay**: Prominently emphasized on the Hero poster above with a multi-layer luminous neon magenta/purple overlay and station nodes (`#A855F7` / `#E879F9`), illustrating how modern rapid transit corridors interconnect historical settlement cores with post-2000 peripheral development zones.
- **Transit Alignment**: High-frequency metro lines provide multi-directional connectivity between the historical core (Pre-1985 settlement) and outer-ring state-level expansion zones (*Kaifaqu* and *Xinqu*).
:::
"""

    transit_attribution = f"""4. **National Railway & Municipal Transit**:
   - **National Passenger Rail Network**: China Railway (中国国家铁路集团 / 12306) and National Railway Administration of China (NRA), covering national high-speed corridors (PDL) and conventional trunk lines.
   - **Urban Subway Network**: AMap (高德地图) Subway Platform and PRC Ministry of Transport (MOT) Urban Rail Transit database ({rail_info['subway_lines_count']} lines, {rail_info['subway_station_count']} stations for {c['name_en']}).""" if has_sub else f"""4. **National Railway Network**: China Railway (中国国家铁路集团 / 12306) & National Railway Administration (NRA) passenger trunk lines and high-speed passenger-dedicated lines (PDL)."""

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

The cartographic poster below maps the physical settlement rings of **{c['name_en']}** across four historical development epochs:

- <span style="color: #F59E0B; font-weight: bold;">● Pre-1985 Core</span>: Historic urban core and initial post-1949 industrial settlements.
- <span style="color: #EF4444; font-weight: bold;">● 1986–1995 Wave</span>: Early reform, opening up, and Deng Xiaoping's 1992 Southern Tour (*Nanxun*).
- <span style="color: #06B6D4; font-weight: bold;">● 1996–2005 Wave</span>: WTO entry, export industrialization, and new development zones (*Kaifaqu*).
- <span style="color: #10B981; font-weight: bold;">● 2006–2015 Wave</span>: High-speed rail expansion, modern new cities (*Xinqu*), and peri-urban consolidation.

::: {{.map-container}}
!['The Urban Growth Rings: {c['name_en']}'](../output/maps/{c_id}_hero.png)
:::
{subway_narrative_block}
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

## 5. Archival Cartography & Wiki Resources

Direct links to open knowledge, semantic geodata, and scanned map collections for **{c['name_en']}**:

- 📖 **English Wikipedia**: [{wiki_res.get('wikipedia_en_title', c['name_en'])}]({wiki_en_url}) — In-depth overview of history, urban development, demographic shifts, and regional governance.
- 🌐 **Chinese Wikipedia (中文维基百科)**: [{wiki_res.get('wikipedia_zh_title', c['name_zh'])}]({wiki_zh_url}) — Authoritative municipal boundaries, administrative subdivisions, and local transport infrastructure.
- 🏷️ **Wikidata Knowledge Base**: [{wikidata_id} ({c['name_en']})]({wikidata_url}) — Semantic knowledge graph entity with geocoordinates, OpenStreetMap tags, and linked administrative entities.
- 🗺️ **Wikimedia Commons Map Repository**: [{wiki_res.get('commons_map_category', 'Maps of ' + c['name_en'])}]({commons_cat_url}) — Community-curated media repository containing thematic, administrative, and transport maps.
{old_map_line}- 🔍 **Scanned Maps & Historical Sheets Search**: [Explore scanned bitmap and topographic maps of {c['name_en']} on Wikimedia Commons]({commons_search_url})

{scanned_maps_box}

---

## 6. Data Sources & Attributions

The quantitative and spatial indicators for **{c['name_en']}** are synthesized from the following primary sources:

1. **Urban Footprint & Built-Up Surface**: German Aerospace Center (DLR) [World Settlement Footprint Evolution (1985–2015)](https://download.geoservice.dlr.de/WSF_EVO/). 30m resolution multi-decadal satellite detection (*Marconcini et al., 2020, Nature Scientific Data*).
2. **Permanent Resident Population**: National Bureau of Statistics of China (NBS), [Seventh National Population Census (第七次全国人口普查 / 七普 2020)](http://www.stats.gov.cn/). Resident population: **{c['pop_million']}M** (National Rank: **#{c['rank_population']}** of 47).
3. **National Urban Tier Classification**: Esri / [ArcGIS Online Big Cities Points FeatureServer](https://services1.arcgis.com/4TXrdeWh0RyCqPgB/arcgis/rest/services/big_cities_points/FeatureServer), National City Rank: **{arc_rank_text}** of 184 major Chinese cities.
{transit_attribution}
5. **Administrative Boundaries**: [GADM Database of Global Administrative Areas (v4.1)](https://gadm.org/), University of California, Davis.
6. **Archival Cartography & Encyclopedia Resources**: [Wikimedia Foundation](https://www.wikimedia.org/) ([Wikipedia](https://en.wikipedia.org/), [Wikidata](https://www.wikidata.org/), and [Wikimedia Commons](https://commons.wikimedia.org/)).

---

{footer_nav}
"""
    with open(f"cities/{c_id}.qmd", "w", encoding="utf-8") as f:
        f.write(qmd_content.strip() + "\n")

print(f"Generated 47 individual Chinese city QMD documents in cities/.")

# ------------------------------------------------------------------------------
# 1B. Generate Individual US Comparison City Pages (Chicago, Milwaukee, Charlotte)
# ------------------------------------------------------------------------------
comp_narratives = {
    "chicago": {
        "title": "Chicago (芝加哥)",
        "subtitle": "US Benchmark Metropolis · Great Lakes Manufacturing & Transit Hub",
        "peer_box": """In 1985, Chicago's built footprint was an immense **1,145.18 km²**—larger than every single Chinese city analyzed in this atlas (e.g., nearly 3× the size of Xi'an or Zhengzhou, and 5.5× the size of Chengdu). Over the subsequent 30 years, Chicago expanded by +204.44 km² (a 1.18× multiplier, 0.55% CAGR).

While Chinese megacities like Xi'an (+961 km², 3.45×) and Wuhan (+798 km², 3.85×) experienced explosive radial outward expansion, Chicago demonstrates the spatial behavior of a mature, post-industrial Western colossus: incremental peripheral edge development, exurban infill along interstate highways and Metra commuter corridors, and gradual demographic consolidation around an already vast urbanized core."""
    },
    "milwaukee": {
        "title": "Milwaukee (密尔沃基)",
        "subtitle": "US Benchmark Metropolis · Great Lakes Legacy Industrial Core",
        "peer_box": """Situated at 43°N latitude on Lake Michigan, Milwaukee shares the cold temperate climate and heavy manufacturing heritage of Northeast China's Rust Belt (Liaoning, Jilin, Heilongjiang). In 1985, Milwaukee possessed a built footprint of **344.94 km²**—comparable in scale to Xi'an (392 km²) and Zhengzhou (316 km²), and significantly larger than Harbin (268 km²) or Fuxin (58 km²).

Between 1985 and 2015, Milwaukee added +91.15 km² to reach 436.09 km² (a 1.26× multiplier, 0.78% CAGR). In stark contrast, Chinese industrial centers facing their own economic restructuring expanded dramatically: Harbin grew 2.62× (+433 km²), Dandong grew 3.12× (+96 km²), and Fuxin grew 2.94× (+112 km²). Milwaukee exemplifies long-term spatial stability in the American Rust Belt."""
    },
    "charlotte": {
        "title": "Charlotte (夏洛特)",
        "subtitle": "US Benchmark Metropolis · Rapid Sunbelt Automobile Sprawl",
        "peer_box": """In 1985, Charlotte's built footprint was **207.98 km²**—virtually identical to Chengdu's **208.06 km²** (a difference of just 0.08 km²!). Both cities entered the mid-1980s as regional centers poised for rapid economic and demographic transformation.

Over the next 30 years, Charlotte became one of the fastest-growing metropolitan areas in the United States, tripling its built footprint to **619.79 km²** (+411.81 km², a 2.98× multiplier, 3.71% CAGR) as the nation's second-largest banking hub. Yet over that exact same period, Chengdu exploded to **1,564.15 km²** (+1,356.09 km², 7.52× multiplier, 6.96% CAGR)—expanding at more than 2.5 times Charlotte's velocity. This direct baseline parallel contrasts the land consumption of American low-density automobile suburbanization with China's high-density transit-oriented metropolitan mega-expansion."""
    }
}

for idx, c in enumerate(comp_cities):
    c_id = c["id"]
    prev_c = comp_cities[idx - 1] if idx > 0 else comp_cities[-1]
    next_c = comp_cities[idx + 1] if idx < len(comp_cities) - 1 else comp_cities[0]
    
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
      <div style="display: inline-block; padding: 0.2rem 0.6rem; background: #0284c7; color: white; border-radius: 4px; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.5rem;">POINT OF COMPARISON (US BENCHMARK)</div>
      <h1 style="color: #ffffff; margin-bottom: 0.25rem;">{c['name_en']} <span style="color: #f59e0b; font-weight: normal;">{c['name_zh']}</span></h1>
      <p style="color: #94a3b8; font-size: 1.1rem; margin: 0;">{c['province_en']}, United States · {c['region']} · Archetype: {c['archetype']}</p>
      <p style="color: #cbd5e1; font-size: 0.95rem; margin-top: 0.35rem;">
        Population: <strong>{c['pop_million']}M</strong> (City Proper) · <strong>{c['pop_metro_million']}M</strong> (Metropolitan Area) · 
        Comparative Peer: <strong>{c['comparative_peer']}</strong>
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
  <a href="../comparison.html" style="color: #f59e0b; text-decoration: none;">↑ All US Comparison Benchmarks</a>
  <a href="{next_c['id']}.html" style="color: #38bdf8; text-decoration: none;">Next: {next_c['name_en']} ({next_c['pop_million']}M) →</a>
</div>
```"""

    corridors_md = ""
    if rail_info.get("major_corridors"):
        corridor_pills = ", ".join(f"`{x}`" for x in rail_info["major_corridors"][:10])
        corridors_md = f"- **Major Railway Lines & Corridors**: {corridor_pills}\n"

    stations_md = ""
    if rail_info.get("key_stations"):
        station_pills = ", ".join(f"`{x}`" for x in rail_info["key_stations"][:10])
        stations_md = f"- **Major Passenger Terminals & Stations**: {station_pills}\n"

    narrative = comp_narratives.get(c_id, {})
    peer_callout = f"""::: {{.callout-note title="Point of Comparison: Benchmark Analysis"}}
{narrative.get('peer_box', '')}
:::"""

    qmd_content = f"""---
title: "{c['name_en']} ({c['name_zh']})"
subtitle: "US Point of Comparison · City Pop: {c['pop_million']}M (Metro: {c['pop_metro_million']}M) · 30-Year Growth: {c['growth_multiple']}× · {c['province_en']}, USA"
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
<div style="font-size: 0.8rem; color: #38bdf8;">Metro CSA: {c['pop_metro_million']}M</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
Metropolitan Archetype
:::
::: {{.metric-val}}
{c['archetype'].split('&')[0].strip()}
:::
<div style="font-size: 0.8rem; color: #94a3b8;">US Growth Profile</div>
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
<div style="font-size: 0.8rem; color: #f59e0b;">30-Year Expansion Ratio</div>
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

{peer_callout}

---

## 1. The Urban Growth Rings (1985–2015)

The cartographic poster below maps the physical settlement expansion of **{c['name_en']}** across the four landmark development epochs:

- <span style="color: #F59E0B; font-weight: bold;">● Pre-1985 Core</span>: Historic urban core and built-up metropolitan area established prior to 1985.
- <span style="color: #EF4444; font-weight: bold;">● 1986–1995 Wave</span>: Late 20th-century suburbanization and commercial arterial growth.
- <span style="color: #06B6D4; font-weight: bold;">● 1996–2005 Wave</span>: Turn-of-the-century suburban expansion, outer-ring residential developments, and exurban employment centers.
- <span style="color: #10B981; font-weight: bold;">● 2006–2015 Wave</span>: Recent outer beltway growth and peri-urban consolidation.

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
### Location in the United States
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

## 5. Archival Cartography & Wiki Resources

Direct links to open knowledge, semantic geodata, and scanned map collections for **{c['name_en']}**:

- 📖 **English Wikipedia**: [{wiki_res.get('wikipedia_en_title', c['name_en'])}]({wiki_en_url}) — In-depth overview of history, urban development, demographic shifts, and regional governance.
- 🌐 **Chinese Wikipedia (中文维基百科)**: [{wiki_res.get('wikipedia_zh_title', c['name_zh'])}]({wiki_zh_url}) — Authoritative municipal boundaries, administrative subdivisions, and local transport infrastructure.
- 🏷️ **Wikidata Knowledge Base**: [{wikidata_id} ({c['name_en']})]({wikidata_url}) — Semantic knowledge graph entity with geocoordinates, OpenStreetMap tags, and linked administrative entities.
- 🗺️ **Wikimedia Commons Map Repository**: [{wiki_res.get('commons_map_category', 'Maps of ' + c['name_en'])}]({commons_cat_url}) — Community-curated media repository containing thematic, administrative, and transport maps.
- 🔍 **Scanned Maps & Historical Sheets Search**: [Explore scanned bitmap and topographic maps of {c['name_en']} on Wikimedia Commons]({commons_search_url})

---

## 6. Data Sources & Attributions

The quantitative and spatial indicators for **{c['name_en']}** are synthesized from the following primary sources:

1. **Urban Footprint & Built-Up Surface**: German Aerospace Center (DLR) [World Settlement Footprint Evolution (1985–2015)](https://download.geoservice.dlr.de/WSF_EVO/). 30m resolution multi-decadal satellite detection (*Marconcini et al., 2020, Nature Scientific Data*).
2. **Resident & Metropolitan Population**: U.S. Census Bureau, [2020 Decennial Census of Population and Housing](https://www.census.gov/). City population: **{c['pop_million']}M**; Metropolitan statistical area: **{c['pop_metro_million']}M**.
3. **Rail & Transit Corridors**: Natural Earth 1:10,000,000 North America Railroads and passenger transit agency records.
4. **Administrative Boundaries**: Natural Earth Admin-1 State and Province Boundaries.
5. **Archival Cartography & Encyclopedia Resources**: [Wikimedia Foundation](https://www.wikimedia.org/) ([Wikipedia](https://en.wikipedia.org/), [Wikidata](https://www.wikidata.org/), and [Wikimedia Commons](https://commons.wikimedia.org/)).

---

{footer_nav}
"""
    with open(f"cities/{c_id}.qmd", "w", encoding="utf-8") as f:
        f.write(qmd_content.strip() + "\n")

print(f"Generated {len(comp_cities)} individual US comparison city QMD documents in cities/.")

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

::: {{.caption-box}}
**Data Sources**: DLR World Settlement Footprint Evolution 30m (Marconcini et al., 2020) · 7th National Population Census of China (2020) · ArcGIS Online Big Cities Points · HOTOSM Railways of China (HDX) · GADM 4.1.
:::
"""
    with open(f"regions/{rk}.qmd", "w", encoding="utf-8") as f:
        f.write(reg_content.strip() + "\n")

print("Generated 6 regional QMD documents in regions/.")

# ------------------------------------------------------------------------------
# 3. Generate Dedicated Global Comparison Page (comparison.qmd)
# ------------------------------------------------------------------------------
comp_cards_html = """```{=html}
<div class="columns" style="display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 2rem;">
  <div style="flex: 1; min-width: 280px; background: #111827; border: 1px solid #1f2937; border-radius: 8px; padding: 1.25rem;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <h3 style="margin: 0; color: #ffffff;"><a href="cities/chicago.html" style="color: #ffffff; text-decoration: none;">Chicago (芝加哥)</a></h3>
      <span class="badge-gold" style="font-size: 0.8rem; padding: 0.2rem 0.5rem; border-radius: 4px;">1.18× Multiplier</span>
    </div>
    <p style="color: #94a3b8; font-size: 0.9rem; margin: 0.5rem 0;">Illinois · Great Lakes Core & Rail Hub · Pop: <strong>2.75M</strong> (Metro: 9.61M)</p>
    <p style="color: #cbd5e1; font-size: 0.85rem; margin-bottom: 0.75rem;">1985 Footprint: <strong>1,145.2 km²</strong> (vast initial baseline) → 2015: <strong>1,349.6 km²</strong> (+204.4 km², 0.55% CAGR). Contrasts with explosive Chinese mega-expansion.</p>
    <a href="cities/chicago.html" class="btn btn-sm" style="color: #38bdf8; text-decoration: none; font-size: 0.85rem; font-weight: 600;">Explore Chicago Map Suite →</a>
  </div>
  <div style="flex: 1; min-width: 280px; background: #111827; border: 1px solid #1f2937; border-radius: 8px; padding: 1.25rem;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <h3 style="margin: 0; color: #ffffff;"><a href="cities/milwaukee.html" style="color: #ffffff; text-decoration: none;">Milwaukee (密尔沃基)</a></h3>
      <span class="badge-gold" style="font-size: 0.8rem; padding: 0.2rem 0.5rem; border-radius: 4px;">1.26× Multiplier</span>
    </div>
    <p style="color: #94a3b8; font-size: 0.9rem; margin: 0.5rem 0;">Wisconsin · Great Lakes Rust Belt · Pop: <strong>0.58M</strong> (Metro: 1.57M)</p>
    <p style="color: #cbd5e1; font-size: 0.85rem; margin-bottom: 0.75rem;">1985 Footprint: <strong>344.9 km²</strong> → 2015: <strong>436.1 km²</strong> (+91.2 km², 0.78% CAGR). Post-industrial stability directly paralleling Northeast China's 43°N belt.</p>
    <a href="cities/milwaukee.html" class="btn btn-sm" style="color: #38bdf8; text-decoration: none; font-size: 0.85rem; font-weight: 600;">Explore Milwaukee Map Suite →</a>
  </div>
  <div style="flex: 1; min-width: 280px; background: #111827; border: 1px solid #1f2937; border-radius: 8px; padding: 1.25rem;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <h3 style="margin: 0; color: #ffffff;"><a href="cities/charlotte.html" style="color: #ffffff; text-decoration: none;">Charlotte (夏洛特)</a></h3>
      <span class="badge-gold" style="font-size: 0.8rem; padding: 0.2rem 0.5rem; border-radius: 4px;">2.98× Multiplier</span>
    </div>
    <p style="color: #94a3b8; font-size: 0.9rem; margin: 0.5rem 0;">North Carolina · Sunbelt Financial Hub · Pop: <strong>0.87M</strong> (Metro: 2.66M)</p>
    <p style="color: #cbd5e1; font-size: 0.85rem; margin-bottom: 0.75rem;">1985 Footprint: <strong>208.0 km²</strong> (identical to Chengdu: 208.1 km²) → 2015: <strong>619.8 km²</strong> (+411.8 km²). Charlotte tripled, but Chengdu surged 7.5× to 1,564 km²!</p>
    <a href="cities/charlotte.html" class="btn btn-sm" style="color: #38bdf8; text-decoration: none; font-size: 0.85rem; font-weight: 600;">Explore Charlotte Map Suite →</a>
  </div>
</div>
```"""

comp_table_rows = """| [Chicago](cities/chicago.html) | 芝加哥 | United States (Illinois) | Mature Industrial Hub | **2.75M** (Metro: 9.61M) | 1,145.18 km² | 1,349.62 km² | +204.44 km² | **1.18×** | 0.55% | Xi'an / Wuhan |
| [Milwaukee](cities/milwaukee.html) | 密尔沃基 | United States (Wisconsin) | Great Lakes Rust Belt | **0.58M** (Metro: 1.57M) | 344.94 km² | 436.09 km² | +91.15 km² | **1.26×** | 0.78% | Northeast Rust Belt (Fuxin / Dandong) |
| [Charlotte](cities/charlotte.html) | 夏洛特 | United States (North Carolina) | Sunbelt Banking Boomtown | **0.87M** (Metro: 2.66M) | 207.98 km² | 619.79 km² | +411.81 km² | **2.98×** | 3.71% | Chengdu (started identical at ~208 km²) |
| [Chengdu](cities/chengdu.html) | 成都市 | China (Sichuan) | Inland Megacity Hub | **20.94M** | 208.06 km² | 1,564.15 km² | +1,356.09 km² | **7.52×** | 6.96% | Charlotte (US Sunbelt Sprawl) |
| [Shenzhen](cities/shenzhen.html) | 深圳市 | China (Guangdong) | Special Economic Zone | **17.56M** | 168.35 km² | 1,064.98 km² | +896.63 km² | **6.33×** | 6.34% | Silicon Valley / Global Tech Capital |
| [Xi'an](cities/xian.html) | 西安市 | China (Shaanxi) | Inland Gateway & Tech Hub | **12.95M** | 392.14 km² | 1,354.03 km² | +961.89 km² | **3.45×** | 4.22% | Chicago / Milwaukee |
| [Wuhan](cities/wuhan.html) | 武汉市 | China (Hubei) | Riverine Megacity & Rail Hub | **12.33M** | 279.63 km² | 1,077.90 km² | +798.27 km² | **3.85×** | 4.60% | Chicago (Midwest Rail Crossroad) |
| [Harbin](cities/harbin.html) | 哈尔滨市 | China (Heilongjiang) | Northern Heavy Industrial Base | **10.01M** | 267.74 km² | 701.48 km² | +433.74 km² | **2.62×** | 3.26% | Milwaukee (Cold Climate Heavy Industry) |
| [Dandong](cities/dandong.html) | 丹东市 | China (Liaoning) | Border Gateway & Port | **2.19M** | 45.20 km² | 140.92 km² | +95.72 km² | **3.12×** | 3.86% | Milwaukee / Great Lakes Ports |
| [Heyuan](cities/heyuan.html) | 河源市 | China (Guangdong) | Pearl River Growth Vanguard | **2.84M** | 15.15 km² | 136.49 km² | +121.34 km² | **9.01×** | 7.60% | Rapid Developing SEZ Hinterland |
"""

comparison_qmd = f"""---
title: "Points of Comparison: US Benchmark Metropolises"
subtitle: "Contrasting China's 30-Year Physical Urban Expansion (1985–2015) Against American Spatial Growth Trajectories"
format:
  html:
    toc: true
---

```{{=html}}
<div class="hero-banner">
  <div style="max-width: 900px;">
    <h1 class="hero-title">Points of Comparison: US Benchmark Metropolises</h1>
    <h2 style="color: #f59e0b; font-size: 1.5rem; margin-top: -0.25rem; margin-bottom: 1rem;">国际城市空间扩展对照研究 · 芝加哥 · 密尔沃基 · 夏洛特</h2>
    <p class="hero-subtitle">
      To contextualize the unprecedented speed, scale, and morphology of China's 30-year urban expansion, this chapter integrates three distinct American metropolitan archetypes—<strong>Chicago</strong>, <strong>Milwaukee</strong>, and <strong>Charlotte</strong>—analyzed using the exact same satellite observation engine: the German Aerospace Center (DLR) World Settlement Footprint Evolution (30m).
    </p>
    <div style="display: flex; gap: 1rem; margin-top: 1.5rem; flex-wrap: wrap;">
      <a href="cities/chicago.html" class="btn btn-primary" style="background: #0284c7; border: none; padding: 0.5rem 1rem; font-weight: 600;">Explore Chicago →</a>
      <a href="cities/milwaukee.html" class="btn btn-primary" style="background: #0284c7; border: none; padding: 0.5rem 1rem; font-weight: 600;">Explore Milwaukee →</a>
      <a href="cities/charlotte.html" class="btn btn-primary" style="background: #0284c7; border: none; padding: 0.5rem 1rem; font-weight: 600;">Explore Charlotte →</a>
      <a href="index.html" class="btn btn-secondary" style="background: #1e293b; color: #cbd5e1; border: 1px solid #334155; padding: 0.5rem 1rem;">Back to National Atlas</a>
    </div>
  </div>
</div>
```

{comp_cards_html}

::: {{.callout-note appearance="simple" icon=true}}
## Methodological Rigor: Uniform Global Satellite Detection
Unlike census boundaries or municipal administrative definitions—which differ radically between nations—the **DLR World Settlement Footprint Evolution (WSF Evolution)** operates on a unified, objective 30-meter physical detection algorithm globally. Every pixel reflects actual imperviously paved and built physical structures detected through joint optical Landsat and radar satellite observations from 1985 to 2015.
:::

## Key Comparative Findings & Analytical Insights

::: {{.metric-grid}}
::: {{.metric-card}}
::: {{.metric-label}}
The Charlotte–Chengdu Baseline
:::
::: {{.metric-val}}
~208 <span style="font-size: 1rem;">km²</span>
:::
<div style="font-size: 0.8rem; color: #f59e0b;">Identical 1985 Footprints</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
The 2015 Divergence
:::
::: {{.metric-val}}
2.5× <span style="font-size: 1rem;">Pace</span>
:::
<div style="font-size: 0.8rem; color: #10b981;">Chengdu 7.52× vs. Charlotte 2.98×</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
Vast Initial Scale
:::
::: {{.metric-val}}
1,145 <span style="font-size: 1rem;">km²</span>
:::
<div style="font-size: 0.8rem; color: #38bdf8;">Chicago 1985 Built Colossus</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
Rust Belt Multiplier
:::
::: {{.metric-val}}
1.26× vs 2.62×
:::
<div style="font-size: 0.8rem; color: #a855f7;">Milwaukee vs. Harbin</div>
:::
:::

---

## 1. The Charlotte vs. Chengdu Paradox

Perhaps the single most illuminating comparison in this entire project is the trajectory of **Charlotte, North Carolina** versus **Chengdu, Sichuan**:

- In **1985**, Charlotte's built settlement footprint was **207.98 km²**.
- In **1985**, Chengdu's built settlement footprint was **208.06 km²**.

The two cities started from a virtually identical physical baseline, separated by less than 0.1 square kilometer. Both functioned as key regional hubs—Chengdu as the historical agricultural and cultural capital of the Sichuan Basin, Charlotte as an emerging Piedmont banking center.

Over the next three decades:
- **Charlotte** became one of the fastest-growing metropolitan economies in the United States, expanding via low-density automobile suburbanization along the I-485 beltway, tripling its built area to **619.79 km²** (+411.81 km², **2.98× multiplier**, **3.71% CAGR**).
- **Chengdu** underwent a monumental densification and concentric multi-ring expansion, constructing five ring roads, the Tianfu New Area, and a 12-line metro system, exploding to **1,564.15 km²** (+1,356.09 km², **7.52× multiplier**, **6.96% CAGR**).

Chengdu added **over three times more new built land** than Charlotte over the identical period, demonstrating how China's transit-oriented, high-density metropolitan expansion operated on an order of magnitude unreachable even by the most aggressive American Sunbelt suburban boomtowns.

---

## 2. Cross-National Expansion Trajectories

The plot below charts the 30-year cumulative built-up area trajectories for Charlotte, Chicago, and Milwaukee plotted directly against key Chinese metropolises (Chengdu, Xi'an, and Dandong):

::: {{.map-container}}
!['The Urban Growth Rings: {c['name_en']}'](../output/maps/{c_id}_hero.png)
:::
{subway_narrative_block}
---

## 3. Growth Multiplier Comparison: American Stability vs. Chinese Speed

How does the relative expansion multiple (2015 footprint ÷ 1985 footprint) compare across national contexts?

::: {{.map-container}}
!['30-Year Growth Multiplier: China Ratlas vs. US Benchmarks'](output/plots/comparison_growth_multipliers.png)
:::

- **American Growth Multipliers**: Clustered narrowly between **1.18×** (Chicago) and **2.98×** (Charlotte). Even rapidly sprawling American cities rarely tripled their built footprint over 1985–2015.
- **Chinese Growth Multipliers**: Distributed across a vastly higher range, from **1.52×** (Korla) up to **9.01×** (Heyuan), with a national median of **3.66×**. Provincial capitals and SEZs routinely multiplied by 4× to 8×.

---

## 4. Master Comparative Matrix (US Benchmarks & Chinese Peers)

The table below contrasts the quantitative spatial indicators of Chicago, Milwaukee, and Charlotte alongside selected Chinese cities spanning diverse regions and growth tiers:

| City | Chinese | Country & Jurisdiction | Growth Archetype | 2020 Population | 1985 Area | 2015 Area | Net Gain | Multiplier | CAGR | Comparative Peer |
|:---|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---|
{comp_table_rows}

---

## 5. Summary of the Three US Benchmark Archetypes

:::: {{.columns}}

::: {{.column width="32%"}}
### Chicago, Illinois
::: {{.map-container}}
!['Chicago Hero Growth Rings'](output/maps/chicago_hero.png)
:::
- **1985 Area**: 1,145.18 km²
- **2015 Area**: 1,349.62 km² (+204.44 km²)
- **Growth Multiple**: **1.18×** (0.55% CAGR)
- **Role**: Established continental colossus. Highlights that Western megacities had already achieved vast physical footprints prior to 1985.
[Full Chicago Page →](cities/chicago.html)
:::

::: {{.column width="32%"}}
### Milwaukee, Wisconsin
::: {{.map-container}}
!['Milwaukee Hero Growth Rings'](output/maps/milwaukee_hero.png)
:::
- **1985 Area**: 344.94 km²
- **2015 Area**: 436.09 km² (+91.15 km²)
- **Growth Multiple**: **1.26×** (0.78% CAGR)
- **Role**: Great Lakes industrial peer to Northeast China. Shows spatial stability during post-industrial economic restructuring.
[Full Milwaukee Page →](cities/milwaukee.html)
:::

::: {{.column width="32%"}}
### Charlotte, North Carolina
::: {{.map-container}}
!['Charlotte Hero Growth Rings'](output/maps/charlotte_hero.png)
:::
- **1985 Area**: 207.98 km²
- **2015 Area**: 619.79 km² (+411.81 km²)
- **Growth Multiple**: **2.98×** (3.71% CAGR)
- **Role**: Sunbelt car-centric sprawl star. Direct counterpart to Chengdu's identical 1985 starting footprint.
[Full Charlotte Page →](cities/charlotte.html)
:::

::::

---

::: {{.caption-box}}
**Data Sources**: German Aerospace Center (DLR) World Settlement Footprint Evolution 30m (Marconcini et al., 2020) · U.S. Census Bureau (2020 Decennial Census) · 7th National Population Census of China (2020) · Natural Earth 10m Railroads · HOTOSM Railways of China.
:::
"""

with open("comparison.qmd", "w", encoding="utf-8") as f:
    f.write(comparison_qmd.strip() + "\n")

print("Generated comparison.qmd successfully!")

# ------------------------------------------------------------------------------
# 4. Generate All Cities Directory (cities.qmd)
# ------------------------------------------------------------------------------
all_rows = ""
for c in cities:
    arc_rank_cell = f"#{c.get('arcgis_rank')}" if c.get('arcgis_rank') else "-"
    all_rows += f"""| #{c['rank_population']} | [{c['name_en']}](cities/{c['id']}.html) | {c['name_zh']} | {c['province_en']} | {c['region']} | **{c['pop_million']}M** | {arc_rank_cell} | {c['area_1985']} km² | {c['area_2015']} km² | +{c['net_gain_km2']} km² | **{c['growth_multiple']}×** | {c['cagr_pct']}% |\n"""

comp_directory_rows = ""
for c in comp_cities:
    comp_directory_rows += f"""| [{c['name_en']}](cities/{c['id']}.html) | {c['name_zh']} | {c['province_en']} (USA) | {c['archetype']} | **{c['pop_million']}M** (Metro: {c['pop_metro_million']}M) | {c['area_1985']} km² | {c['area_2015']} km² | +{c['net_gain_km2']} km² | **{c['growth_multiple']}×** | {c['cagr_pct']}% | {c['comparative_peer']} |\n"""

cities_qmd = f"""---
title: "All 47 Cities Directory"
subtitle: "Complete 30-Year Urban Growth Inventory Ordered by Population (2020 Census) & International Benchmarks"
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

## International Points of Comparison: US Benchmark Metropolises

To provide international context for the scale, velocity, and morphology of China's urban growth, three United States metropolises were analyzed using the exact same DLR WSF Evolution 30m satellite methodology:

- **[Chicago](cities/chicago.html)**: Mature industrial giant and continental rail hub (1.18× multiplier).
- **[Milwaukee](cities/milwaukee.html)**: Historic Great Lakes manufacturing center sharing the 43°N latitude with Northeast China (1.26× multiplier).
- **[Charlotte](cities/charlotte.html)**: Sunbelt banking boomtown that began in 1985 with the exact same built footprint as Chengdu (~208 km²), but grew at less than half Chengdu's eventual pace (2.98× vs 7.52×).

For an in-depth cross-national analysis, visit the **[US Points of Comparison](comparison.html)** chapter.

| City | Chinese | State / Country | Metro Archetype | Population (2020) | 1985 Area | 2015 Area | Net Gain | Multiplier | CAGR | Comparative Peer |
|:---|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---|
{comp_directory_rows}

---

::: {{.caption-box}}
**Data Sources**: DLR World Settlement Footprint Evolution 30m (Marconcini et al., 2020) · 7th National Population Census of China (2020) · U.S. Census Bureau (2020) · ArcGIS Online Big Cities Points · China Railway 12306 (NRA) · AMap (高德地图) Subway Platform · Natural Earth 10m Railroads · GADM 4.1.
:::
"""
with open("cities.qmd", "w", encoding="utf-8") as f:
    f.write(cities_qmd.strip() + "\n")

print("Generated cities.qmd successfully!")

# ------------------------------------------------------------------------------
# 5. Generate Academic Methodology Page (methodology.qmd)
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

### B. China National Railway & Municipal Subway Datasets
- **National Passenger Railway Network**:
  - **Data Custodians**: China Railway (中国国家铁路集团 / 12306) and National Railway Administration of the PRC (国家铁路局).
  - **Coverage**: Complete national network of 432 operational passenger railway corridors, covering high-speed lines (350 / 300 / 250 km/h PDL), intercity railways, and electrified conventional trunk lines across 3,300 passenger stations.
  - **Spatial Processing**: Topology-cleaned and topologically verified WGS-84 vector geometry and train stop sequences from 12306 schedules (`data/raw/china_railway_12306_lines.geojson` and `data/raw/china_railway_12306_stations.geojson`).
- **Municipal Subway & Rapid Transit Networks**:
  - **Data Custodian**: AMap (高德地图) Subway Platform and PRC Ministry of Transport (MOT) Urban Rail Transit database.
  - **Coverage**: Complete operational rapid transit systems for all 15 atlas cities with active subways (Chengdu, Shenzhen, Xi'an, Zhengzhou, Wuhan, Shijiazhuang, Harbin, Jinan, Kunming, Nanchang, Xiamen, Lanzhou, Urumqi, Wuhu, and Hohhot).
  - **Coordinate Calibration**: Converted from GCJ-02 cartographic coordinates to ellipsoidal WGS-84 (`data/processed/city_subways/<city>_subway.geojson`).
- **Citation & License**:
  > China Railway 12306 & National Railway Administration (2024). *China Railway Passenger Service System [Data set]*. AMap (高德地图) Subway Platform (2024). Open Database License / Public Service Cartographic Data.

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

### G. International Benchmark Datasets (US Comparison Cities)
- **Data Sources**: 
  - **U.S. Census Bureau (2020 Decennial Census)**: Resident population for incorporated city proper limits and Combined Statistical Areas (CSA) / Metropolitan Statistical Areas (MSA).
  - **Natural Earth (1:10,000,000 Vector Theme)**: North American railroads line vectors and state boundaries (*ne_10m_railroads_north_america* and *ne_110m_admin_1_states_provinces*).
  - **DLR WSF Evolution 30m Global Coverage**: The identical global satellite settlement detection rasters cropped across Chicago, Milwaukee, and Charlotte bounding boxes, ensuring absolute mathematical and sensor parity.

---

## 2. Data Licensing & Terms of Use

| Dataset | Provider | License / Terms of Use | Attribution Notice |
|:---|:---|:---|:---|
| **WSF Evolution** | German Aerospace Center (DLR) | Creative Commons Attribution 4.0 International (CC-BY 4.0) | © DLR (2020, 2021) |
| **National Railways** | China Railway 12306 / NRA | Public Service & Transport Open Data | © China Railway (CR) / 12306 / NRA |
| **City Subways** | AMap (高德地图) / MOT PRC | Public Transit API / Cartographic Service | © AMap (高德地图) / Ministry of Transport |
| **Big Cities Points** | Esri / ArcGIS Online | Esri Public REST Feature Service Terms | © Esri, ArcGIS Online Content Providers |
| **National Census (2020)** | National Bureau of Statistics (NBS) | Public Statistical Release / Government Open Data | Source: National Bureau of Statistics of China |
| **US Census (2020)** | U.S. Census Bureau | Public Domain (U.S. Government Work) | Source: U.S. Census Bureau |
| **Natural Earth Rail** | Natural Earth Vector | Public Domain | Source: Natural Earth |
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

print("Generated methodology.qmd successfully!")

# ------------------------------------------------------------------------------
# 6. Generate Home Page (index.qmd + Comparison Callout & Attributions Table)
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
      This ratlas maps the spatial morphology, expansion rings, China Railway (12306) and municipal subway networks, and quantitative growth trajectories across <strong>47 diverse Chinese cities</strong> ranked by population, with global benchmarks in <strong>Chicago, Milwaukee, and Charlotte</strong>.
    </p>
    <div style="display: flex; gap: 1rem; margin-top: 1.5rem; flex-wrap: wrap;">
      <a href="cities.html" class="btn btn-primary" style="background: #0284c7; border: none; padding: 0.6rem 1.25rem; font-weight: 600;">Browse All 47 Cities →</a>
      <a href="comparison.html" class="btn btn-primary" style="background: #f59e0b; color: #0b0f19; border: none; padding: 0.6rem 1.25rem; font-weight: 600;">US Comparisons (Chicago, Milwaukee, Charlotte) →</a>
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
Total Chinese Cities
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
Rail & Transit
:::
::: {{.metric-val}}
12306 / AMap
:::
<div style="font-size: 0.8rem; color: #38bdf8;">432 National Lines + 15 Metro Cities</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
US Benchmarks
:::
::: {{.metric-val}}
3 Cities
:::
<div style="font-size: 0.8rem; color: #f59e0b;">Chicago, Milwaukee, Charlotte</div>
:::
:::

---

## National Urban Expansion & HOTOSM Railways Map

The map below displays all 47 cities in the ratlas across China, sized by **2020 Census Population**, colored by **30-year growth multiplier**, overlaid with the **HOTOSM China Railways dataset (HDX)** and contextualized with **ArcGIS Online Big Cities Points**:

::: {{.map-container}}
!['China Urban Growth Ratlas National Overview & HOTOSM Railways'](output/maps/china_overview_map.png)
:::

---

## Global Points of Comparison: US Benchmark Metropolises

How did China's 30-year urban expansion compare to Western metropolitan development? 
To establish an objective international baseline, **Milwaukee**, **Chicago**, and **Charlotte** were incorporated into the ratlas using the exact same DLR WSF Evolution 30m satellite data:

::: {{.columns}}

::: {{.column width="32%"}}
::: {{.region-card}}
### [Chicago (芝加哥)](cities/chicago.html)
**Mature Great Lakes Core** · Pop: **2.75M** (Metro: 9.61M)
- **1985 Footprint**: 1,145.2 km² (larger than all 47 Chinese cities in 1985)
- **2015 Footprint**: 1,349.6 km² (+204.4 km²)
- **30-Year Multiplier**: <strong style="color: #38bdf8;">1.18×</strong> (CAGR: 0.55%)
- **Comparative Peer**: Xi'an / Wuhan

[Explore Chicago Maps & Analytics →](cities/chicago.html)
:::
:::

::: {{.column width="32%"}}
::: {{.region-card}}
### [Milwaukee (密尔沃基)](cities/milwaukee.html)
**Great Lakes Rust Belt** · Pop: **0.58M** (Metro: 1.57M)
- **1985 Footprint**: 344.9 km² (comparable to Xi'an / Zhengzhou)
- **2015 Footprint**: 436.1 km² (+91.2 km²)
- **30-Year Multiplier**: <strong style="color: #38bdf8;">1.26×</strong> (CAGR: 0.78%)
- **Comparative Peer**: Northeast Rust Belt (Fuxin / Dandong)

[Explore Milwaukee Maps & Analytics →](cities/milwaukee.html)
:::
:::

::: {{.column width="32%"}}
::: {{.region-card}}
### [Charlotte (夏洛特)](cities/charlotte.html)
**Sunbelt Boomtown** · Pop: **0.87M** (Metro: 2.66M)
- **1985 Footprint**: 208.0 km² (virtually identical to Chengdu: 208.1 km²)
- **2015 Footprint**: 619.8 km² (+411.8 km²)
- **30-Year Multiplier**: <strong style="color: #f59e0b;">2.98×</strong> (CAGR: 3.71%)
- **Comparative Peer**: Chengdu (7.52× vs. Charlotte 2.98×)

[Explore Charlotte Maps & Analytics →](cities/charlotte.html)
:::
:::

:::

::: {{.map-container}}
!['Cross-National Expansion Trajectories: China vs. US Benchmarks'](output/plots/china_vs_us_comparison.png)
:::

[Read the Complete Cross-National Analysis in the US Comparisons Chapter →](comparison.html)

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
| **National Railways (12306 / NRA)** | China Railway & National Railway Administration | Vector / 432 Lines, 3,300 Stations | National passenger rail backbone, high-speed lines & stations | China Railway 12306 Service System & NRA (2024) |
| **City Subway Systems (AMap)** | AMap (高德地图) & MOT PRC | Vector / 15 Cities | Rapid transit network lines & stations for all metro-served cities | [AMap Subway Platform](http://map.amap.com/subway/index.html) · Ministry of Transport |
| **Big Cities Points Layer** | Esri / ArcGIS Online | Vector Points / 184 Cities | National city hierarchy ranking (1–200) and tier-1 anchor points | [ArcGIS FeatureServer](https://services1.arcgis.com/4TXrdeWh0RyCqPgB/arcgis/rest/services/big_cities_points/FeatureServer) |
| **Seventh National Population Census (七普 2020)** | National Bureau of Statistics of China (NBS) | Prefectural / 2020 | Primary ranking order (#1–#47) by permanent resident population | [NBS China Census Bulletin (2021)](http://www.stats.gov.cn/) |
| **US Decennial Census (2020)** | U.S. Census Bureau | Municipal & Metro / 2020 | Population benchmarks for Chicago, Milwaukee, and Charlotte | [U.S. Census Bureau](https://www.census.gov/) |
| **North America Railroads (10m)** | Natural Earth Vector | Vector / Continental | Rail networks for US comparison benchmark cities | [Natural Earth](https://www.naturalearthdata.com/) |
| **GADM Administrative Areas (v4.1)** | University of California, Davis (UCD) | Levels 0, 1, 2 / National | Administrative boundary clipping and bilingual toponymy | [GADM v4.1](https://gadm.org/) · Hijmans et al. (2022) |

---

::: {{.caption-box}}
**China Urban Growth Ratlas** · Built with R (`terra`, `sf`, `ggplot2`, `tidyterra`, `patchwork`) and Quarto. Data: German Aerospace Center (DLR) World Settlement Footprint Evolution (30m), 7th National Population Census (七普 2020), U.S. Census Bureau (2020), China Railway 12306 Network (NRA), AMap (高德地图) Subway Platform, Natural Earth, ArcGIS Online Big Cities Points & GADM 4.1.
:::
"""

with open("index.qmd", "w", encoding="utf-8") as f:
    f.write(index_qmd.strip() + "\n")

print("Generated all Quarto source documents successfully with comprehensive source citations!")
