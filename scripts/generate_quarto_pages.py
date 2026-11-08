import json, os, re

# Load processed data
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

with open("data/processed/city_agsl_scans_mapping.json", "r", encoding="utf-8") as f:
    agsl_mapping = json.load(f)

with open("data/processed/gdrive_agsl_scans.json", "r", encoding="utf-8") as f:
    all_agsl_scans = json.load(f)

cities = sorted(cities, key=lambda x: x["rank_population"])

GDRIVE_FOLDER_URL = "https://drive.google.com/drive/folders/1b-HupghVS7KQn4ZTvGjfOHFFMgPnH2KV?usp=sharing"

def build_agsl_block(city_id, city_name):
    scans = agsl_mapping.get(city_id, [])
    if not scans:
        return f"""<div class="agsl-box">
  <div class="agsl-title">Archival cartography: AGSL historical map scans</div>
  <div class="agsl-desc">
    High-resolution historical map sheets, military topographic surveys, and municipal town plans from the <strong>American Geographical Society Library (AGSL)</strong> archive collection provide crucial ground-truth spatial morphology predating modern satellite observation.
  </div>
  <div style="margin-top: 0.5rem;">
    <a href="{GDRIVE_FOLDER_URL}" target="_blank" rel="noopener" class="resource-btn" style="font-weight: 600;">Browse complete AGSL historical map scans folder on Google Drive ({len(all_agsl_scans)} sheets) →</a>
  </div>
</div>"""
    
    cards = []
    for s in scans:
        fname = s["title"]
        file_url = s["url"]
        clean_name = fname.replace("@", " ").replace("_", " ").replace(".png", "").replace(".jpg", "").replace(".JPG", "")
        clean_name = clean_name.capitalize()
        cards.append(f"""    <div class="agsl-card">
      <div>
        <a href="{file_url}" target="_blank" rel="noopener">📄 {clean_name}</a>
      </div>
      <span class="agsl-tag">AGSL Scan</span>
    </div>""")
    
    cards_html = "\n".join(cards)
    return f"""<div class="agsl-box">
  <div class="agsl-title">Archival cartography: AGSL historical map scans</div>
  <div class="agsl-desc">
    The following high-resolution archival sheets and historical surveys from the <strong>American Geographical Society Library (AGSL)</strong> collection directly cover <strong>{city_name}</strong> and its surrounding territorial hinterland:
  </div>
  <div class="agsl-grid">
{cards_html}
  </div>
  <div style="margin-top: 1rem;">
    <a href="{GDRIVE_FOLDER_URL}" target="_blank" rel="noopener" class="resource-btn" style="font-weight: 600;">Browse complete AGSL archive on Google Drive ({len(all_agsl_scans)} total scans) →</a>
  </div>
</div>"""

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
# 1. Generate Individual Chinese City Pages (Map-Forward + AGSL Scans)
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

    arc_rank_val = c.get("arcgis_rank")
    arc_rank_text = f"#{arc_rank_val}" if arc_rank_val else "N/A"
    
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
    subway_badge = f'<span class="metric-badge badge-blue" style="font-size: 0.85rem; margin-left: 0.5rem;">🚇 {rail_info.get("subway_lines_count")} Metro Lines</span>' if has_sub else ""
    wiki_res = wiki_resources.get(c_id, {})

    wiki_en_url = wiki_res.get("wikipedia_en_url", f"https://en.wikipedia.org/wiki/{c['name_en']}")
    wiki_zh_url = wiki_res.get("wikipedia_zh_url", f"https://zh.wikipedia.org/wiki/{c['name_zh']}")
    wikidata_id = wiki_res.get("wikidata_id", "Q")
    wikidata_url = wiki_res.get("wikidata_url", "https://www.wikidata.org")
    commons_cat_url = wiki_res.get("commons_map_category_url", f"https://commons.wikimedia.org/wiki/Category:Maps_of_{c['name_en']}")
    commons_search_url = wiki_res.get("commons_search_maps_url", f"https://commons.wikimedia.org/w/index.php?search={c['name_en']}+map")

    agsl_block = build_agsl_block(c_id, c["name_en"])

    hero_block = f"""```{{=html}}
<div class="hero-banner">
  <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
    <div>
      <h1 class="hero-title" style="margin-bottom: 0.25rem;">{c['name_en']} <span style="color: #1e3f34; font-style: normal; font-weight: normal;">{c['name_zh']}</span> {subway_badge}</h1>
      <p style="color: #5e524a; font-size: 1.1rem; margin: 0; font-style: italic;">{c['pinyin']} · {c['province_en']} ({c['province_zh']}) · {c['region']}</p>
      <p style="color: #221d1a; font-size: 0.95rem; margin-top: 0.35rem;">
        Permanent population: <strong>{c['pop_million']} million</strong> (2020 census) · 
        Population rank: <strong>#{c['rank_population']}</strong> of 47 · 
        ArcGIS urban hierarchy rank: <strong>{arc_rank_text}</strong>
      </p>
      <div style="margin-top: 0.75rem; display: flex; flex-wrap: wrap; gap: 0.5rem;">
        <a href="{wiki_en_url}" target="_blank" rel="noopener" class="resource-btn">Wikipedia (EN)</a>
        <a href="{wiki_zh_url}" target="_blank" rel="noopener" class="resource-btn">维基百科 (ZH)</a>
        <a href="{wikidata_url}" target="_blank" rel="noopener" class="resource-btn">Wikidata ({wikidata_id})</a>
        <a href="{commons_cat_url}" target="_blank" rel="noopener" class="resource-btn">Wikimedia Commons</a>
        <a href="{commons_search_url}" target="_blank" rel="noopener" class="resource-btn">Scanned maps search</a>
        <a href="{GDRIVE_FOLDER_URL}" target="_blank" rel="noopener" class="resource-btn" style="background: #e8ded1; border-color: #943324; font-weight: 600;">AGSL map scans archive ↗</a>
      </div>
    </div>
    <div style="text-align: right;">
      <span class="metric-badge badge-gold" style="font-size: 1.1rem; padding: 0.5rem 1rem;">{c['growth_multiple']}× growth multiple</span>
    </div>
  </div>
</div>
```"""

    footer_nav = f"""```{{=html}}
<div style="display: flex; justify-content: space-between; margin-top: 2rem; padding: 1rem; background: #f4efe4; border: 1px solid #d6ccbe; border-radius: 4px;">
  <a href="{prev_c['id']}.html" style="color: #943324; text-decoration: none; font-weight: 600;">← Previous: {prev_c['name_en']} ({prev_c['pop_million']}M)</a>
  <a href="../regions/{reg_file.replace('.qmd', '.html')}" style="color: #1e3f34; text-decoration: none; font-weight: 600;">↑ {c['region']}</a>
  <a href="{next_c['id']}.html" style="color: #943324; text-decoration: none; font-weight: 600;">Next: {next_c['name_en']} ({next_c['pop_million']}M) →</a>
</div>
```"""

    corridors_md = ""
    if rail_info.get("major_corridors"):
        corridor_pills = ", ".join(f"`{x}`" for x in rail_info["major_corridors"][:10])
        corridors_md = f"- **Major railway lines & corridors**: {corridor_pills}\n"

    stations_md = ""
    if rail_info.get("key_stations"):
        station_pills = ", ".join(f"`{x}`" for x in rail_info["key_stations"][:10])
        stations_md = f"- **Major passenger terminals & stations**: {station_pills}\n"

    old_map_line = ""
    if wiki_res.get("commons_old_map_category_url"):
        old_map_line = f"- 📜 **Historical maps collection**: [{wiki_res['commons_old_map_category']}]({wiki_res['commons_old_map_category_url']}) — Scanned historical maps, municipal plans, and early surveys.\n"

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

- **Key metro corridors**: {lines_preview}
- **Cartographic overlay**: Illustrated on the main poster above, connecting historical settlement cores with peripheral development zones.
- **Transit alignment**: High-frequency metro corridors provide multi-directional connectivity between the historical core (Pre-1985 settlement) and outer-ring state-level expansion zones (*Kaifaqu* and *Xinqu*).
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

## 1. The urban growth rings (1985–2015)

The cartographic monograph below documents the physical settlement rings of **{c['name_en']}** across four historical development epochs:

- <span style="color: #c75c3d; font-weight: bold;">● Pre-1985 Core</span>: Historic urban core and initial post-1949 industrial settlements.
- <span style="color: #2e5a48; font-weight: bold;">● 1986–1995 Wave</span>: Early reform, opening up, and Deng Xiaoping's 1992 Southern Tour (*Nanxun*).
- <span style="color: #457b9d; font-weight: bold;">● 1996–2005 Wave</span>: WTO entry, export industrialization, and new development zones (*Kaifaqu*).
- <span style="color: #e9c46a; font-weight: bold;">● 2006–2015 Wave</span>: High-speed rail expansion, modern new cities (*Xinqu*), and peri-urban consolidation.

::: {{.map-container}}
!['The urban growth rings: {c['name_en']}'](../output/maps/{c_id}_hero.png)
:::
{subway_narrative_block}

```{{=html}}
{agsl_block}
```

---

## 2. Four-epoch footprint progression

Uniform-scale physical footprint progression maps tracking built-up settlement expansion over time:

::: {{.map-container}}
!['Small multiples footprint progression: {c['name_en']}'](../output/maps/{c_id}_small_multiples.png)
:::

---

## 3. Geographical location & expansion trajectory

:::: {{.columns}}

::: {{.column width="48%"}}
### Location in China
::: {{.map-container}}
!['Regional inset: {c['name_en']}'](../output/maps/{c_id}_context.png)
:::
:::

::: {{.column width="4%"}}
:::

::: {{.column width="48%"}}
### Thirty-year expansion curve
::: {{.map-container}}
!['Expansion trajectory: {c['name_en']}'](../output/plots/{c_id}_trajectory.png)
:::
:::

::::

---

## 4. Urban expansion & hierarchy indicators

::: {{.metric-grid}}
::: {{.metric-card}}
::: {{.metric-label}}
2020 Population
:::
::: {{.metric-val}}
{c['pop_million']} <span style="font-size: 1rem; color: #5e524a;">M</span>
:::
<div style="font-size: 0.8rem; color: #943324;">Pop Rank #{c['rank_population']} of 47</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
ArcGIS City Rank
:::
::: {{.metric-val}}
{arc_rank_text}
:::
<div style="font-size: 0.8rem; color: #5e524a;">National Big Cities Tier</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
1985 Baseline Area
:::
::: {{.metric-val}}
{c['area_1985']} <span style="font-size: 1rem; color: #5e524a;">km²</span>
:::
:::

::: {{.metric-card}}
::: {{.metric-label}}
2015 Urban Footprint
:::
::: {{.metric-val}}
{c['area_2015']} <span style="font-size: 1rem; color: #5e524a;">km²</span>
:::
<div style="font-size: 0.8rem; color: #1e3f34;">+{c['net_gain_km2']} km²</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
Growth Multiple
:::
::: {{.metric-val}}
{c['growth_multiple']}×
:::
<div style="font-size: 0.8rem; color: #943324;">Multiplier Rank #{c['rank_multiplier']}</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
Annual Growth (CAGR)
:::
::: {{.metric-val}}
{c['cagr_pct']}%
:::
<div style="font-size: 0.8rem; color: #5e524a;">1985–2015</div>
:::
:::

---

## 5. Five-year milestone chronology

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

## 6. Archival cartography & wiki resources

Direct links to open knowledge, semantic geodata, and scanned map collections for **{c['name_en']}**:

- 📖 **English Wikipedia**: [{wiki_res.get('wikipedia_en_title', c['name_en'])}]({wiki_en_url}) — In-depth overview of history, urban development, demographic shifts, and regional governance.
- 🌐 **Chinese Wikipedia (中文维基百科)**: [{wiki_res.get('wikipedia_zh_title', c['name_zh'])}]({wiki_zh_url}) — Authoritative municipal boundaries, administrative subdivisions, and local transport infrastructure.
- 🏷️ **Wikidata Knowledge Base**: [{wikidata_id} ({c['name_en']})]({wikidata_url}) — Semantic knowledge graph entity with geocoordinates, OpenStreetMap tags, and linked administrative entities.
- 🗺️ **Wikimedia Commons Map Repository**: [{wiki_res.get('commons_map_category', 'Maps of ' + c['name_en'])}]({commons_cat_url}) — Community-curated media repository containing thematic, administrative, and transport maps.
{old_map_line}- 🔍 **Scanned Maps & Historical Sheets Search**: [Explore scanned bitmap and topographic maps of {c['name_en']} on Wikimedia Commons]({commons_search_url})
- 🗄️ **AGSL Historical Map Archive**: [Access Google Drive repository of AGSL scans]({GDRIVE_FOLDER_URL})

{scanned_maps_box}

---

## 7. Sources & methodology attributions

The quantitative and spatial indicators for **{c['name_en']}** are synthesized from the following primary sources:

1. **Urban Footprint & Built-Up Surface**: German Aerospace Center (DLR) [World Settlement Footprint Evolution (1985–2015)](https://download.geoservice.dlr.de/WSF_EVO/). 30m resolution multi-decadal satellite detection (*Marconcini et al., 2020, Nature Scientific Data*).
2. **Permanent Resident Population**: National Bureau of Statistics of China (NBS), [Seventh National Population Census (第七次全国人口普查 / 七普 2020)](http://www.stats.gov.cn/). Resident population: **{c['pop_million']}M** (National Rank: **#{c['rank_population']}** of 47).
3. **National Urban Tier Classification**: Esri / [ArcGIS Online Big Cities Points FeatureServer](https://services1.arcgis.com/4TXrdeWh0RyCqPgB/arcgis/rest/services/big_cities_points/FeatureServer), National City Rank: **{arc_rank_text}** of 184 major Chinese cities.
{transit_attribution}
5. **Administrative Boundaries**: [GADM Database of Global Administrative Areas (v4.1)](https://gadm.org/), University of California, Davis.
6. **Archival Cartography & Historical Surveys**: American Geographical Society Library (AGSL) Map Collection & [Wikimedia Foundation](https://www.wikimedia.org/) ([Wikipedia](https://en.wikipedia.org/), [Wikidata](https://www.wikidata.org/), and [Wikimedia Commons](https://commons.wikimedia.org/)).

---

{footer_nav}
"""
    with open(f"cities/{c_id}.qmd", "w", encoding="utf-8") as f:
        f.write(qmd_content.strip() + "\n")

print("Generated 47 Chinese city pages with map-forward layout & AGSL callouts!")

# ------------------------------------------------------------------------------
# 1B. Generate US Comparison City Pages
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
      <div style="display: inline-block; padding: 0.2rem 0.6rem; background: #943324; color: white; border-radius: 3px; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.5rem; font-family: -apple-system, sans-serif;">Point of comparison · US benchmark</div>
      <h1 class="hero-title" style="margin-bottom: 0.25rem;">{c['name_en']} <span style="color: #1e3f34; font-weight: normal; font-style: normal;">{c['name_zh']}</span></h1>
      <p style="color: #5e524a; font-size: 1.1rem; margin: 0; font-style: italic;">{c['province_en']}, United States · {c['region']} · Archetype: {c['archetype']}</p>
      <p style="color: #221d1a; font-size: 0.95rem; margin-top: 0.35rem;">
        Population: <strong>{c['pop_million']}M</strong> (City proper) · <strong>{c['pop_metro_million']}M</strong> (Metropolitan area) · 
        Comparative peer: <strong>{c['comparative_peer']}</strong>
      </p>
      <div style="margin-top: 0.75rem; display: flex; flex-wrap: wrap; gap: 0.5rem;">
        <a href="{wiki_en_url}" target="_blank" rel="noopener" class="resource-btn">Wikipedia (EN)</a>
        <a href="{wiki_zh_url}" target="_blank" rel="noopener" class="resource-btn">维基百科 (ZH)</a>
        <a href="{wikidata_url}" target="_blank" rel="noopener" class="resource-btn">Wikidata ({wikidata_id})</a>
        <a href="{commons_cat_url}" target="_blank" rel="noopener" class="resource-btn">Wikimedia Commons</a>
        <a href="{commons_search_url}" target="_blank" rel="noopener" class="resource-btn">Scanned maps search</a>
        <a href="{GDRIVE_FOLDER_URL}" target="_blank" rel="noopener" class="resource-btn" style="background: #e8ded1; border-color: #943324; font-weight: 600;">AGSL map scans archive ↗</a>
      </div>
    </div>
    <div style="text-align: right;">
      <span class="metric-badge badge-gold" style="font-size: 1.1rem; padding: 0.5rem 1rem;">{c['growth_multiple']}× growth multiple</span>
    </div>
  </div>
</div>
```"""

    footer_nav = f"""```{{=html}}
<div style="display: flex; justify-content: space-between; margin-top: 2rem; padding: 1rem; background: #f4efe4; border: 1px solid #d6ccbe; border-radius: 4px;">
  <a href="{prev_c['id']}.html" style="color: #943324; text-decoration: none; font-weight: 600;">← Previous: {prev_c['name_en']} ({prev_c['pop_million']}M)</a>
  <a href="../comparison.html" style="color: #1e3f34; text-decoration: none; font-weight: 600;">↑ All US comparison benchmarks</a>
  <a href="{next_c['id']}.html" style="color: #943324; text-decoration: none; font-weight: 600;">Next: {next_c['name_en']} ({next_c['pop_million']}M) →</a>
</div>
```"""

    corridors_md = ""
    if rail_info.get("major_corridors"):
        corridor_pills = ", ".join(f"`{x}`" for x in rail_info["major_corridors"][:10])
        corridors_md = f"- **Major railway lines & corridors**: {corridor_pills}\n"

    stations_md = ""
    if rail_info.get("key_stations"):
        station_pills = ", ".join(f"`{x}`" for x in rail_info["key_stations"][:10])
        stations_md = f"- **Major passenger terminals & stations**: {station_pills}\n"

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

## 1. The urban expansion rings (1985–2015)

The cartographic monograph below maps the physical settlement expansion of **{c['name_en']}** across four landmark development epochs:

- <span style="color: #c75c3d; font-weight: bold;">● Pre-1985 Core</span>: Historic urban core and built-up metropolitan area established prior to 1985.
- <span style="color: #2e5a48; font-weight: bold;">● 1986–1995 Wave</span>: Late 20th-century suburbanization and commercial arterial growth.
- <span style="color: #457b9d; font-weight: bold;">● 1996–2005 Wave</span>: Turn-of-the-century suburban expansion, outer-ring residential developments, and exurban employment centers.
- <span style="color: #e9c46a; font-weight: bold;">● 2006–2015 Wave</span>: Recent outer beltway growth and peri-urban consolidation.

::: {{.map-container}}
!['The urban growth rings: {c['name_en']}'](../output/maps/{c_id}_hero.png)
:::

{peer_callout}

---

## 2. Four-epoch footprint progression

Uniform-scale physical footprint progression maps tracking built-up settlement expansion over time:

::: {{.map-container}}
!['Small multiples footprint progression: {c['name_en']}'](../output/maps/{c_id}_small_multiples.png)
:::

---

## 3. Geographical location & expansion trajectory

:::: {{.columns}}

::: {{.column width="48%"}}
### Location in the United States
::: {{.map-container}}
!['Regional inset: {c['name_en']}'](../output/maps/{c_id}_context.png)
:::
:::

::: {{.column width="4%"}}
:::

::: {{.column width="48%"}}
### Thirty-year expansion curve
::: {{.map-container}}
!['Expansion trajectory: {c['name_en']}'](../output/plots/{c_id}_trajectory.png)
:::
:::

::::

---

## 4. Urban expansion & hierarchy indicators

::: {{.metric-grid}}
::: {{.metric-card}}
::: {{.metric-label}}
2020 Population
:::
::: {{.metric-val}}
{c['pop_million']} <span style="font-size: 1rem; color: #5e524a;">M</span>
:::
<div style="font-size: 0.8rem; color: #943324;">Metro CSA: {c['pop_metro_million']}M</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
Metropolitan Archetype
:::
::: {{.metric-val}}
{c['archetype'].split('&')[0].strip()}
:::
<div style="font-size: 0.8rem; color: #5e524a;">US Growth Profile</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
1985 Baseline Area
:::
::: {{.metric-val}}
{c['area_1985']} <span style="font-size: 1rem; color: #5e524a;">km²</span>
:::
:::

::: {{.metric-card}}
::: {{.metric-label}}
2015 Urban Footprint
:::
::: {{.metric-val}}
{c['area_2015']} <span style="font-size: 1rem; color: #5e524a;">km²</span>
:::
<div style="font-size: 0.8rem; color: #1e3f34;">+{c['net_gain_km2']} km²</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
Growth Multiple
:::
::: {{.metric-val}}
{c['growth_multiple']}×
:::
<div style="font-size: 0.8rem; color: #943324;">30-Year Expansion Ratio</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
Annual Growth (CAGR)
:::
::: {{.metric-val}}
{c['cagr_pct']}%
:::
<div style="font-size: 0.8rem; color: #5e524a;">1985–2015</div>
:::
:::

---

## 5. Five-year milestone chronology

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

## 6. Archival cartography & historical map scans

Direct links to open knowledge, semantic geodata, and scanned map collections for **{c['name_en']}**:

- 📖 **English Wikipedia**: [{wiki_res.get('wikipedia_en_title', c['name_en'])}]({wiki_en_url}) — In-depth overview of history, urban development, demographic shifts, and regional governance.
- 🌐 **Chinese Wikipedia (中文维基百科)**: [{wiki_res.get('wikipedia_zh_title', c['name_zh'])}]({wiki_zh_url}) — Authoritative municipal boundaries, administrative subdivisions, and local transport infrastructure.
- 🏷️ **Wikidata Knowledge Base**: [{wikidata_id} ({c['name_en']})]({wikidata_url}) — Semantic knowledge graph entity with geocoordinates, OpenStreetMap tags, and linked administrative entities.
- 🗺️ **Wikimedia Commons Map Repository**: [{wiki_res.get('commons_map_category', 'Maps of ' + c['name_en'])}]({commons_cat_url}) — Community-curated media repository containing thematic, administrative, and transport maps.
- 🔍 **Scanned Maps & Historical Sheets Search**: [Explore scanned bitmap and topographic maps of {c['name_en']} on Wikimedia Commons]({commons_search_url})
- 🗄️ **AGSL Historical Map Archive**: [Access Google Drive repository of AGSL scans]({GDRIVE_FOLDER_URL})

---

## 7. Sources & methodology attributions

The quantitative and spatial indicators for **{c['name_en']}** are synthesized from the following primary sources:

1. **Urban Footprint & Built-Up Surface**: German Aerospace Center (DLR) [World Settlement Footprint Evolution (1985–2015)](https://download.geoservice.dlr.de/WSF_EVO/). 30m resolution multi-decadal satellite detection (*Marconcini et al., 2020, Nature Scientific Data*).
2. **Resident & Metropolitan Population**: U.S. Census Bureau, [2020 Decennial Census of Population and Housing](https://www.census.gov/). City population: **{c['pop_million']}M**; Metropolitan statistical area: **{c['pop_metro_million']}M**.
3. **Rail & Transit Corridors**: Natural Earth 1:10,000,000 North America Railroads and passenger transit agency records.
4. **Administrative Boundaries**: Natural Earth Admin-1 State and Province Boundaries.
5. **Archival Cartography & Historical Surveys**: American Geographical Society Library (AGSL) Map Collection & [Wikimedia Foundation](https://www.wikimedia.org/) ([Wikipedia](https://en.wikipedia.org/), [Wikidata](https://www.wikidata.org/), and [Wikimedia Commons](https://commons.wikimedia.org/)).

---

{footer_nav}
"""
    with open(f"cities/{c_id}.qmd", "w", encoding="utf-8") as f:
        f.write(qmd_content.strip() + "\n")

print("Generated US comparison city pages!")

# ------------------------------------------------------------------------------
# 2. Regional Pages
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
**{c['province_en']} Province** · Population: <strong style="color: #943324;">{c['pop_million']} Million</strong> (Rank #{c['rank_population']}) · ArcGIS Hierarchy Rank: <strong>{arc_rank_cell}</strong> · 30-Year Multiplier: <strong style="color: #1e3f34;">{c['growth_multiple']}×</strong>

- **1985 Footprint**: {c['area_1985']} km²
- **2015 Footprint**: {c['area_2015']} km² (Net expansion: +{c['net_gain_km2']} km²)
- **Compound Annual Growth Rate**: {c['cagr_pct']}%/year

[View Maps & Visual Suite →](../cities/{c['id']}.html)
:::
"""

    reg_hero = f"""```{{=html}}
<div class="hero-banner">
  <h1 class="hero-title" style="margin-bottom: 0.5rem;">{rv['title']} <span style="color: #1e3f34; font-weight: normal; font-style: normal;">{rv['title_zh']}</span></h1>
  <p class="hero-subtitle">{rv['desc']}</p>
  <div style="margin-top: 1rem;">
    <a href="{GDRIVE_FOLDER_URL}" target="_blank" rel="noopener" class="resource-btn" style="background: #e8ded1; border-color: #943324; font-weight: 600;">Browse AGSL historical scans for this region ↗</a>
  </div>
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

## Regional member cities (ranked by population)

| Pop Rank | City | Chinese | Province | Population | ArcGIS Rank | 1985 Area | 2015 Area | Net Gain | Multiplier | CAGR |
|:---:|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
{rows}

---

## Member city profiles

{city_links}

---

::: {{.caption-box}}
**Data Sources**: DLR World Settlement Footprint Evolution 30m (Marconcini et al., 2020) · 7th National Population Census of China (2020) · ArcGIS Online Big Cities Points · HOTOSM Railways of China (HDX) · GADM 4.1 · American Geographical Society Library (AGSL).
:::
"""
    with open(f"regions/{rk}.qmd", "w", encoding="utf-8") as f:
        f.write(reg_content.strip() + "\n")

print("Generated 6 regional pages!")

# ------------------------------------------------------------------------------
# 3. Global Comparison Page
# ------------------------------------------------------------------------------
comp_cards_html = f"""```{{=html}}
<div class="columns" style="display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 2rem;">
  <div style="flex: 1; min-width: 280px; background: #f4efe4; border: 1px solid #d6ccbe; border-radius: 4px; padding: 1.25rem;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <h3 style="margin: 0; color: #943324;"><a href="cities/chicago.html" style="color: #943324; text-decoration: none;">Chicago (芝加哥)</a></h3>
      <span class="badge-gold" style="font-size: 0.8rem; padding: 0.2rem 0.5rem; border-radius: 3px;">1.18× Multiplier</span>
    </div>
    <p style="color: #5e524a; font-size: 0.9rem; margin: 0.5rem 0;">Illinois · Great Lakes Core & Rail Hub · Pop: <strong>2.75M</strong> (Metro: 9.61M)</p>
    <p style="color: #221d1a; font-size: 0.85rem; margin-bottom: 0.75rem;">1985 Footprint: <strong>1,145.2 km²</strong> (vast initial baseline) → 2015: <strong>1,349.6 km²</strong> (+204.4 km², 0.55% CAGR). Contrasts with explosive Chinese mega-expansion.</p>
    <a href="cities/chicago.html" style="color: #943324; font-weight: 600; font-size: 0.85rem;">Explore Chicago Map Suite →</a>
  </div>
  <div style="flex: 1; min-width: 280px; background: #f4efe4; border: 1px solid #d6ccbe; border-radius: 4px; padding: 1.25rem;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <h3 style="margin: 0; color: #943324;"><a href="cities/milwaukee.html" style="color: #943324; text-decoration: none;">Milwaukee (密尔沃基)</a></h3>
      <span class="badge-gold" style="font-size: 0.8rem; padding: 0.2rem 0.5rem; border-radius: 3px;">1.26× Multiplier</span>
    </div>
    <p style="color: #5e524a; font-size: 0.9rem; margin: 0.5rem 0;">Wisconsin · Great Lakes Rust Belt · Pop: <strong>0.58M</strong> (Metro: 1.57M)</p>
    <p style="color: #221d1a; font-size: 0.85rem; margin-bottom: 0.75rem;">1985 Footprint: <strong>344.9 km²</strong> → 2015: <strong>436.1 km²</strong> (+91.2 km², 0.78% CAGR). Post-industrial stability directly paralleling Northeast China's 43°N belt.</p>
    <a href="cities/milwaukee.html" style="color: #943324; font-weight: 600; font-size: 0.85rem;">Explore Milwaukee Map Suite →</a>
  </div>
  <div style="flex: 1; min-width: 280px; background: #f4efe4; border: 1px solid #d6ccbe; border-radius: 4px; padding: 1.25rem;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <h3 style="margin: 0; color: #943324;"><a href="cities/charlotte.html" style="color: #943324; text-decoration: none;">Charlotte (夏洛特)</a></h3>
      <span class="badge-gold" style="font-size: 0.8rem; padding: 0.2rem 0.5rem; border-radius: 3px;">2.98× Multiplier</span>
    </div>
    <p style="color: #5e524a; font-size: 0.9rem; margin: 0.5rem 0;">North Carolina · Sunbelt Financial Hub · Pop: <strong>0.87M</strong> (Metro: 2.66M)</p>
    <p style="color: #221d1a; font-size: 0.85rem; margin-bottom: 0.75rem;">1985 Footprint: <strong>208.0 km²</strong> (identical to Chengdu: 208.1 km²) → 2015: <strong>619.8 km²</strong> (+411.8 km²). Charlotte tripled, but Chengdu surged 7.5× to 1,564 km²!</p>
    <a href="cities/charlotte.html" style="color: #943324; font-weight: 600; font-size: 0.85rem;">Explore Charlotte Map Suite →</a>
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
    <h2 style="color: #1e3f34; font-size: 1.4rem; margin-top: -0.25rem; margin-bottom: 1rem; font-weight: normal; font-style: normal;">国际城市空间扩展对照研究 · 芝加哥 · 密尔沃基 · 夏洛特</h2>
    <p class="hero-subtitle">
      To contextualize the unprecedented speed, scale, and morphology of China's 30-year urban expansion, this chapter integrates three distinct American metropolitan archetypes—<strong>Chicago</strong>, <strong>Milwaukee</strong>, and <strong>Charlotte</strong>—analyzed using the exact same satellite observation engine: the German Aerospace Center (DLR) World Settlement Footprint Evolution (30m).
    </p>
    <div style="display: flex; gap: 0.75rem; margin-top: 1.5rem; flex-wrap: wrap;">
      <a href="cities/chicago.html" class="resource-btn">Explore Chicago →</a>
      <a href="cities/milwaukee.html" class="resource-btn">Explore Milwaukee →</a>
      <a href="cities/charlotte.html" class="resource-btn">Explore Charlotte →</a>
      <a href="{GDRIVE_FOLDER_URL}" target="_blank" rel="noopener" class="resource-btn" style="background: #e8ded1; border-color: #943324; font-weight: 600;">Browse AGSL map scans repository (Google Drive) ↗</a>
      <a href="index.html" class="resource-btn">Back to national atlas</a>
    </div>
  </div>
</div>
```

{comp_cards_html}

::: {{.callout-note appearance="simple" icon=true}}
## Methodological rigor: Uniform global satellite detection
Unlike census boundaries or municipal administrative definitions—which differ radically between nations—the **DLR World Settlement Footprint Evolution (WSF Evolution)** operates on a unified, objective 30-meter physical detection algorithm globally. Every pixel reflects actual imperviously paved and built physical structures detected through joint optical Landsat and radar satellite observations from 1985 to 2015.
:::

## 1. Cross-national expansion trajectories

The plot below charts the 30-year cumulative built-up area trajectories for Charlotte, Chicago, and Milwaukee plotted directly against key Chinese metropolises (Chengdu, Xi'an, and Dandong):

::: {{.map-container}}
!['Cross-national expansion trajectories: China vs. US benchmarks'](output/plots/china_vs_us_comparison.png)
:::

---

## 2. The Charlotte vs. Chengdu paradox

Perhaps the single most illuminating comparison in this entire project is the trajectory of **Charlotte, North Carolina** versus **Chengdu, Sichuan**:

- In **1985**, Charlotte's built settlement footprint was **207.98 km²**.
- In **1985**, Chengdu's built settlement footprint was **208.06 km²**.

The two cities started from a virtually identical physical baseline, separated by less than 0.1 square kilometer. Both functioned as key regional hubs—Chengdu as the historical agricultural and cultural capital of the Sichuan Basin, Charlotte as an emerging Piedmont banking center.

Over the next three decades:
- **Charlotte** became one of the fastest-growing metropolitan economies in the United States, expanding via low-density automobile suburbanization along the I-485 beltway, tripling its built area to **619.79 km²** (+411.81 km², **2.98× multiplier**, **3.71% CAGR**).
- **Chengdu** underwent a monumental densification and concentric multi-ring expansion, constructing five ring roads, the Tianfu New Area, and a 12-line metro system, exploding to **1,564.15 km²** (+1,356.09 km², **7.52× multiplier**, **6.96% CAGR**).

Chengdu added **over three times more new built land** than Charlotte over the identical period, demonstrating how China's transit-oriented, high-density metropolitan expansion operated on an order of magnitude unreachable even by the most aggressive American Sunbelt suburban boomtowns.

---

## 3. Growth multiplier comparison: American stability vs. Chinese speed

How does the relative expansion multiple (2015 footprint ÷ 1985 footprint) compare across national contexts?

::: {{.map-container}}
!['Thirty-year growth multipliers: China ratlas vs. US benchmarks'](output/plots/comparison_growth_multipliers.png)
:::

- **American Growth Multipliers**: Clustered narrowly between **1.18×** (Chicago) and **2.98×** (Charlotte). Even rapidly sprawling American cities rarely tripled their built footprint over 1985–2015.
- **Chinese Growth Multipliers**: Distributed across a vastly higher range, from **1.52×** (Korla) up to **9.01×** (Heyuan), with a national median of **3.66×**. Provincial capitals and SEZs routinely multiplied by 4× to 8×.

---

## 4. Master comparative matrix (US benchmarks & Chinese peers)

The table below contrasts the quantitative spatial indicators of Chicago, Milwaukee, and Charlotte alongside selected Chinese cities spanning diverse regions and growth tiers:

| City | Chinese | Country & Jurisdiction | Growth Archetype | 2020 Population | 1985 Area | 2015 Area | Net Gain | Multiplier | CAGR | Comparative Peer |
|:---|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---|
{comp_table_rows}

---

## 5. Summary of the three US benchmark archetypes

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
**Data Sources**: German Aerospace Center (DLR) World Settlement Footprint Evolution 30m (Marconcini et al., 2020) · U.S. Census Bureau (2020 Decennial Census) · 7th National Population Census of China (2020) · Natural Earth 10m Railroads · American Geographical Society Library (AGSL) · HOTOSM Railways of China.
:::
"""

with open("comparison.qmd", "w", encoding="utf-8") as f:
    f.write(comparison_qmd.strip() + "\n")

print("Generated comparison.qmd!")

# ------------------------------------------------------------------------------
# 4. Generate All Cities Directory (cities.qmd)
# ------------------------------------------------------------------------------
all_city_rows = ""
for c in cities:
    arc_rank_val = c.get("arcgis_rank", "-")
    all_city_rows += f"""| #{c['rank_population']} | [{c['name_en']}]({c['id']}.html) | {c['name_zh']} | {c['province_en']} | {c['region']} | **{c['pop_million']}M** | {arc_rank_val} | {c['area_1985']} km² | {c['area_2015']} km² | +{c['net_gain_km2']} km² | **{c['growth_multiple']}×** | {c['cagr_pct']}% |\n"""

cities_qmd = f"""---
title: "The 47 Chinese Metropolises: Master Directory"
subtitle: "Comprehensive Index of all 47 Cities Ranked Strictly by Permanent Resident Population (2020 Census)"
format:
  html:
    toc: true
---

```{{=html}}
<div class="hero-banner">
  <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
    <div>
      <h1 class="hero-title" style="margin-bottom: 0.25rem;">Complete 47-City Master Registry</h1>
      <p class="hero-subtitle">
        Strictly ordered from #1 (Chengdu, 20.9M) to #47 (Hunchun, 0.24M). Every city is paired with uniform-scale DLR satellite footprint progression maps, China Railway 12306 passenger networks, and AGSL historical map scans.
      </p>
      <div style="margin-top: 0.75rem;">
        <a href="{GDRIVE_FOLDER_URL}" target="_blank" rel="noopener" class="resource-btn" style="background: #e8ded1; border-color: #943324; font-weight: 600;">Browse AGSL historical scans repository on Google Drive ↗</a>
      </div>
    </div>
    <div>
      <span class="metric-badge badge-gold" style="font-size: 1.1rem; padding: 0.5rem 1rem;">47 Cities Surveyed</span>
    </div>
  </div>
</div>
```

## Complete 47-city master index

| Pop Rank | City | Chinese | Province | Geographic Region | 2020 Population | ArcGIS Rank | 1985 Area | 2015 Area | Net Gain | Growth Multiple | CAGR |
|:---:|:---|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
{all_city_rows}

---

::: {{.callout-note title="US Points of Comparison"}}
For an in-depth cross-national analysis, visit the **[US Points of Comparison](comparison.html)** chapter comparing **Chicago**, **Milwaukee**, and **Charlotte** against their Chinese peers.
:::

::: {{.caption-box}}
**Data Sources**: DLR World Settlement Footprint Evolution 30m (Marconcini et al., 2020) · 7th National Population Census of China (2020) · ArcGIS Online Big Cities Points · HOTOSM Railways of China (HDX) · GADM 4.1 · American Geographical Society Library (AGSL).
:::
"""
with open("cities.qmd", "w", encoding="utf-8") as f:
    f.write(cities_qmd.strip() + "\n")

print("Generated cities.qmd!")

# ------------------------------------------------------------------------------
# 5. Generate Home Page (index.qmd)
# ------------------------------------------------------------------------------
index_hero = f"""```{{=html}}
<div class="hero-banner">
  <div style="max-width: 900px;">
    <h1 class="hero-title">China Urban Growth Ratlas</h1>
    <h2 style="color: #1e3f34; font-size: 1.4rem; margin-top: -0.25rem; margin-bottom: 1rem; font-weight: normal; font-style: normal;">中国城市空间扩展图集 · 1985–2015</h2>
    <p class="hero-subtitle">
      Between 1985 and 2015, the People's Republic of China underwent the largest physical urbanization process in human history. 
      This ratlas maps the spatial morphology, expansion rings, China Railway (12306) and municipal subway networks, and quantitative growth trajectories across <strong>47 diverse Chinese cities</strong> ranked by population, with global benchmarks in <strong>Chicago, Milwaukee, and Charlotte</strong>, accompanied by historical map plates from the <strong>American Geographical Society Library (AGSL)</strong>.
    </p>
    <div style="display: flex; gap: 0.75rem; margin-top: 1.5rem; flex-wrap: wrap;">
      <a href="cities.html" class="resource-btn" style="background: #943324; color: #fff; border-color: #943324; font-weight: 600;">Browse all 47 cities →</a>
      <a href="comparison.html" class="resource-btn" style="background: #1e3f34; color: #fff; border-color: #1e3f34; font-weight: 600;">US comparisons (Chicago, Milwaukee, Charlotte) →</a>
      <a href="{GDRIVE_FOLDER_URL}" target="_blank" rel="noopener" class="resource-btn" style="background: #e8ded1; border-color: #943324; font-weight: 600;">AGSL historical map scans (Google Drive) ↗</a>
      <a href="methodology.html" class="resource-btn">Methodology & citations</a>
    </div>
  </div>
</div>
```"""

selection_callout = """::: {.callout-note appearance="simple" icon=true}
## Scope & sample selection: Excluding Tier-1 superstar megacities
The 47 cities in this atlas were deliberately selected to **exclude China's absolute largest tier-1 megacities** (specifically Beijing, Shanghai, Guangzhou, Chongqing, and Tianjin).

By centering on dynamic provincial capitals (e.g., Chengdu, Wuhan, Xi'an, Zhengzhou), specialized manufacturing nodes (e.g., Shenzhen, Zhuhai, Taizhou, Zibo), ancient Silk Road oases (e.g., Kashgar, Hotan, Wuwei), and strategic border gateways (e.g., Dandong, Hunchun), this ratlas examines how physical urbanization and infrastructure modernization transformed the full depth of China's urban hierarchy beyond the global superstar metropolises.
:::"""

imagemap_html = """```{=html}
<div style="position: relative; width: 100%; max-width: 1100px; margin: 1.5rem auto; border-radius: 4px; overflow: hidden; border: 1px solid #d6ccbe; box-shadow: 0 4px 14px rgba(34,29,26,0.1);">
  <!-- Base Regional Map Graphic -->
  <img src="output/maps/china_regions_map.png" usemap="#chinaregions" alt="China Geographic Regions Map" style="width: 100%; height: auto; display: block;">

  <!-- Interactive SVG Clickable Overlay with Glowing Regions -->
  <svg viewBox="0 0 1600 1100" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: auto;">
    <style>
      .reg-link { cursor: pointer; transition: all 0.25s ease; }
      .reg-poly { fill: transparent; stroke: transparent; stroke-width: 3; transition: all 0.25s ease; }
      .reg-link:hover .reg-poly { fill: rgba(148, 51, 36, 0.25); stroke: #943324; }
      .reg-link text { fill: #ffffff; font-size: 26px; font-weight: bold; text-anchor: middle; pointer-events: none; opacity: 0.95; text-shadow: 0 2px 6px rgba(0,0,0,0.9); font-family: "Hoefler Text", Georgia, serif; }
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

agsl_showcase_section = f"""```{{=html}}
<div class="agsl-box">
  <div class="agsl-title">Archival cartography: AGSL historical map collection</div>
  <div class="agsl-desc">
    This monograph integrates a dedicated curated selection of high-resolution historical scans from the <strong>American Geographical Society Library (AGSL)</strong>, featuring city guides, early Republican plans, British War Office surveys, and late-twentieth-century municipal transit maps for Chengdu, Harbin, Jinan, Kashgar, Korla, Lanzhou, Shijiazhuang, Urumqi, Weihai, Wuhan, Xiamen, and Xi'an.
  </div>
  <div style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
    <a href="{GDRIVE_FOLDER_URL}" target="_blank" rel="noopener" class="resource-btn" style="background: #943324; color: #fff; font-weight: 600;">Browse all {len(all_agsl_scans)} AGSL scans on Google Drive ↗</a>
    <a href="cities/harbin.html" class="resource-btn">Harbin historical plates (1946–2001) →</a>
    <a href="cities/xian.html" class="resource-btn">Xi'an historical surveys (1986–2000) →</a>
    <a href="cities/chengdu.html" class="resource-btn">Chengdu Michelin & snack maps →</a>
  </div>
</div>
```"""

index_qmd = f"""---
title: "China Urban Growth Ratlas (1985–2015)"
subtitle: "A Geospatial Exploration of 30 Years of Physical Expansion Across 47 Chinese Metropolises"
format:
  html:
    toc: true
---

{index_hero}

{selection_callout}

## 1. National urban expansion & passenger rail network

The map below displays all 47 cities in the ratlas across China, sized by **2020 Census Population**, colored by **30-year growth multiplier**, overlaid with the **HOTOSM China Railways dataset (HDX)** and contextualized with **ArcGIS Online Big Cities Points**:

::: {{.map-container}}
!['China urban growth ratlas national overview and passenger railways'](output/maps/china_overview_map.png)
:::

---

## 2. Archival map plates & historical scans

{agsl_showcase_section}

---

## 3. High-speed rail network & urban hierarchy

China's High-Speed Rail grid physically stitched together regional capitals and secondary nodes, accelerating post-2005 outward expansion across the 184 major urban centers identified in the ArcGIS Online Big Cities layer:

::: {{.map-container}}
!['High-speed rail network and urban hierarchy'](output/maps/china_hsr_overview.png)
:::

---

## 4. Key findings & national overview

::: {{.metric-grid}}
::: {{.metric-card}}
::: {{.metric-label}}
Total Chinese Cities
:::
::: {{.metric-val}}
47
:::
<div style="font-size: 0.8rem; color: #943324;">Ranked by Population</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
Largest City (2020)
:::
::: {{.metric-val}}
20.9 <span style="font-size: 1rem;">M</span>
:::
<div style="font-size: 0.8rem; color: #1e3f34;">Chengdu (成都市)</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
Peak Growth Multiple
:::
::: {{.metric-val}}
9.0×
:::
<div style="font-size: 0.8rem; color: #1e3f34;">Heyuan (河源市)</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
Peak Area Expansion
:::
::: {{.metric-val}}
+1,356 <span style="font-size: 1rem;">km²</span>
:::
<div style="font-size: 0.8rem; color: #1e3f34;">Chengdu (成都市)</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
Rail & Transit
:::
::: {{.metric-val}}
12306 / AMap
:::
<div style="font-size: 0.8rem; color: #943324;">432 National Lines + 15 Metro Cities</div>
:::

::: {{.metric-card}}
::: {{.metric-label}}
US Benchmarks
:::
::: {{.metric-val}}
3 Cities
:::
<div style="font-size: 0.8rem; color: #1e3f34;">Chicago, Milwaukee, Charlotte</div>
:::
:::

---

## 5. Global points of comparison: US benchmark metropolises

How did China's 30-year urban expansion compare to Western metropolitan development? 
To establish an objective international baseline, **Milwaukee**, **Chicago**, and **Charlotte** were incorporated into the ratlas using the exact same DLR WSF Evolution 30m satellite data:

::: {{.columns}}

::: {{.column width="32%"}}
::: {{.region-card}}
### [Chicago (芝加哥)](cities/chicago.html)
**Mature Great Lakes Core** · Pop: **2.75M** (Metro: 9.61M)
- **1985 Footprint**: 1,145.2 km² (larger than all 47 Chinese cities in 1985)
- **2015 Footprint**: 1,349.6 km² (+204.4 km²)
- **30-Year Multiplier**: <strong style="color: #943324;">1.18×</strong> (CAGR: 0.55%)
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
- **30-Year Multiplier**: <strong style="color: #943324;">1.26×</strong> (CAGR: 0.78%)
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
- **30-Year Multiplier**: <strong style="color: #1e3f34;">2.98×</strong> (CAGR: 3.71%)
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

## 6. Thirty-year growth multiplier rankings

Which cities experienced the highest relative spatial expansion between 1985 and 2015?

::: {{.map-container}}
!['Top 25 Cities by 30-Year Urban Growth Multiple'](output/plots/national_growth_ranking.png)
:::

---

## 7. Interactive regional explorations

Select any region on the interactive map below to jump directly to its dedicated regional chapter, or explore via the region cards below:

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

## 8. Primary data sources & citations

This atlas synthesizes open geospatial and authoritative statistical datasets. Detailed academic citations, licensing terms, and analytical documentation are available in the [Methodology & Citations](methodology.html) chapter.

| Dataset / Source | Custodian / Provider | Resolution / Coverage | Analytical Role in Ratlas | Primary Citation / Access |
|:---|:---|:---|:---|:---|
| **World Settlement Footprint Evolution (WSF Evolution)** | German Aerospace Center (DLR) | 30m / 1985–2015 Annual | Primary spatial engine; identifies exact year of settlement detection | [DLR Geoservice](https://download.geoservice.dlr.de/WSF_EVO/) · Marconcini et al. (2020, *Sci. Data*) |
| **National Railways (12306 / NRA)** | China Railway & National Railway Administration | Vector / 432 Lines, 3,300 Stations | National passenger rail backbone, high-speed lines & stations | China Railway 12306 Service System & NRA (2024) |
| **City Subway Systems (AMap)** | AMap (高德地图) & MOT PRC | Vector / 15 Cities | Rapid transit network lines & stations for all metro-served cities | [AMap Subway Platform](http://map.amap.com/subway/index.html) · Ministry of Transport |
| **Big Cities Points Layer** | Esri / ArcGIS Online | Vector Points / 184 Cities | National city hierarchy ranking (1–200) and tier-1 anchor points | [ArcGIS FeatureServer](https://services1.arcgis.com/4TXrdeWh0RyCqPgB/arcgis/rest/services/big_cities_points/FeatureServer) |
| **Seventh National Population Census (七普 2020)** | National Bureau of Statistics of China (NBS) | Prefectural / 2020 | Primary ranking order (#1–#47) by permanent resident population | [NBS China Census Bulletin (2021)](http://www.stats.gov.cn/) |
| **AGSL Historical Map Archive** | American Geographical Society Library (AGSL) | Scanned Sheets / High-Res | Archival ground-truth topographic sheets and municipal town plans | [AGSL Collection (Google Drive)]({GDRIVE_FOLDER_URL}) |
| **US Decennial Census (2020)** | U.S. Census Bureau | Municipal & Metro / 2020 | Population benchmarks for Chicago, Milwaukee, and Charlotte | [U.S. Census Bureau](https://www.census.gov/) |
| **North America Railroads (10m)** | Natural Earth Vector | Vector / Continental | Rail networks for US comparison benchmark cities | [Natural Earth](https://www.naturalearthdata.com/) |
| **GADM Administrative Areas (v4.1)** | University of California, Davis (UCD) | Levels 0, 1, 2 / National | Administrative boundary clipping and bilingual toponymy | [GADM v4.1](https://gadm.org/) · Hijmans et al. (2022) |

---

::: {{.caption-box}}
**China Urban Growth Ratlas** · Built with R (`terra`, `sf`, `ggplot2`, `tidyterra`, `patchwork`) and Quarto. Data: German Aerospace Center (DLR) World Settlement Footprint Evolution (30m), 7th National Population Census (七普 2020), U.S. Census Bureau (2020), China Railway 12306 Network (NRA), AMap (高德地图) Subway Platform, Natural Earth, American Geographical Society Library (AGSL), ArcGIS Online Big Cities Points & GADM 4.1.
:::
"""

with open("index.qmd", "w", encoding="utf-8") as f:
    f.write(index_qmd.strip() + "\n")

print("Generated index.qmd successfully!")
