import json, math, os, csv

COMPARISON_CITIES = [
    {
        "id": "chicago",
        "name_en": "Chicago",
        "name_zh": "芝加哥",
        "pinyin": "Zhījiāgē",
        "province_en": "Illinois",
        "province_zh": "伊利诺伊州",
        "country": "United States",
        "region": "US Midwest & Great Lakes",
        "lat": 41.8781,
        "lon": -87.6298,
        "radius_km": 30,
        "archetype": "Mature Industrial Metropolis & Transit Capital",
        "pop_million": 2.75,
        "pop_metro_million": 9.61,
        "pop_exact": 2746388,
        "pop_note": "City proper (2020 US Census; Metro CSA: 9.61M)",
        "comparative_peer": "Xi'an / Wuhan / Harbin",
        "key_insight": "In 1985, Chicago's built footprint (1,145 km²) was larger than any of the 47 Chinese cities. Over 30 years, it added +204 km² (1.18×, 0.55% CAGR), exemplifying mature, incremental expansion in a dense, rail-centric global metropolis."
    },
    {
        "id": "milwaukee",
        "name_en": "Milwaukee",
        "name_zh": "密尔沃基",
        "pinyin": "Mì'ěrwòjī",
        "province_en": "Wisconsin",
        "province_zh": "威斯康星州",
        "country": "United States",
        "region": "US Great Lakes Rust Belt",
        "lat": 43.0389,
        "lon": -87.9065,
        "radius_km": 20,
        "archetype": "Legacy Manufacturing Center & Post-Industrial Core",
        "pop_million": 0.58,
        "pop_metro_million": 1.57,
        "pop_exact": 577222,
        "pop_note": "City proper (2020 US Census; Metro MSA: 1.57M)",
        "comparative_peer": "Northeast Rust Belt (Fuxin / Dandong / Tieling)",
        "key_insight": "Sharing the 43°N latitude and industrial manufacturing heritage with Northeast China, Milwaukee had a 1985 built footprint (345 km²) comparable to Xi'an or Zhengzhou. However, its post-industrial growth was modest (+91 km², 1.26×, 0.78% CAGR), contrasting sharply with Chinese industrial centers that tripled or quadrupled."
    },
    {
        "id": "charlotte",
        "name_en": "Charlotte",
        "name_zh": "夏洛特",
        "pinyin": "Xiàluòtè",
        "province_en": "North Carolina",
        "province_zh": "北卡罗来纳州",
        "country": "United States",
        "region": "US Sunbelt & Southeast",
        "lat": 35.2271,
        "lon": -80.8431,
        "radius_km": 25,
        "archetype": "Rapid Sunbelt Sprawl & Banking Center",
        "pop_million": 0.87,
        "pop_metro_million": 2.66,
        "pop_exact": 874579,
        "pop_note": "City proper (2020 US Census; Metro CSA: 2.66M)",
        "comparative_peer": "Chengdu",
        "key_insight": "In 1985, Charlotte's built footprint (208.00 km²) was virtually identical to Chengdu (208.06 km²). Over 30 years, Charlotte tripled its footprint to 620 km² (+412 km², 2.98×, 3.71% CAGR)—one of the fastest-growing US Sunbelt metros. Yet Chengdu exploded to 1,564 km² (7.52×), illustrating the sheer divergence between American suburban automobile sprawl and Chinese high-density transit-oriented mega-expansion."
    }
]

for c in COMPARISON_CITIES:
    lat = c["lat"]
    lon = c["lon"]
    rad_km = c["radius_km"]
    dlat = rad_km / 111.0
    dlon = rad_km / (111.0 * math.cos(math.radians(lat)))
    c["bbox"] = [
        round(lon - dlon, 4),
        round(lat - dlat, 4),
        round(lon + dlon, 4),
        round(lat + dlat, 4)
    ]
    lon_min_tile = 2 * math.floor(c["bbox"][0] / 2)
    lon_max_tile = 2 * math.floor(c["bbox"][2] / 2)
    lat_min_tile = 2 * math.floor(c["bbox"][1] / 2)
    lat_max_tile = 2 * math.floor(c["bbox"][3] / 2)
    tiles = []
    for tlon in range(lon_min_tile, lon_max_tile + 2, 2):
        for tlat in range(lat_min_tile, lat_max_tile + 2, 2):
            tiles.append(f"WSFevolution_v1_{tlon}_{tlat}")
    c["wsf_tiles"] = sorted(list(set(tiles)))

os.makedirs("data", exist_ok=True)
with open("data/comparison_cities.json", "w", encoding="utf-8") as f:
    json.dump(COMPARISON_CITIES, f, ensure_ascii=False, indent=2)

with open("data/comparison_cities.csv", "w", newline="", encoding="utf-8") as f:
    fieldnames = [
        "id", "name_en", "name_zh", "pinyin", "province_en", "province_zh",
        "country", "region", "lat", "lon", "radius_km", "archetype",
        "pop_million", "pop_metro_million", "pop_exact", "pop_note",
        "comparative_peer", "bbox", "wsf_tiles"
    ]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in COMPARISON_CITIES:
        r = dict(row)
        r["bbox"] = ",".join(map(str, r["bbox"]))
        r["wsf_tiles"] = ";".join(r["wsf_tiles"])
        del r["key_insight"]
        writer.writerow(r)

print(f"Written data/comparison_cities.json and data/comparison_cities.csv ({len(COMPARISON_CITIES)} cities).")
