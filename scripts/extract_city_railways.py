import json, os, re

def main():
    print("Loading city definitions...")
    with open("data/cities.json", "r", encoding="utf-8") as f:
        cities = json.load(f)

    # City bounding boxes with a small buffer (~0.05 degrees)
    city_boxes = {}
    for c in cities:
        cid = c["id"]
        bbox = c["bbox"] # [min_lon, min_lat, max_lon, max_lat]
        city_boxes[cid] = {
            "bbox": (bbox[0] - 0.05, bbox[1] - 0.05, bbox[2] + 0.05, bbox[3] + 0.05),
            "name_en": c["name_en"],
            "name_zh": c["name_zh"]
        }

    city_rails = {c["id"]: [] for c in cities}
    city_stations = {c["id"]: [] for c in cities}

    raw_geojson = "data/raw/hotosm_railways/railways.geojson"
    if not os.path.exists(raw_geojson):
        print(f"Error: {raw_geojson} not found!")
        return

    print(f"Streaming and extracting features from {raw_geojson}...")
    hsr_patterns = ["高铁", "客专", "高速", "城际", "磁浮"]
    hsr_en_patterns = ["high-speed", "pdl", "intercity", "maglev", "express"]

    feature_count = 0
    with open(raw_geojson, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith('{ "type": "Feature"'):
                continue
            feature_count += 1
            if feature_count % 100000 == 0:
                print(f"Processed {feature_count:,} features...")

            feat = json.loads(line.rstrip(','))
            geom = feat.get("geometry")
            if not geom:
                continue

            gtype = geom.get("type")
            coords = geom.get("coordinates")
            props = feat.get("properties", {})
            rw = props.get("railway")

            if rw == "station" and gtype == "Point":
                lon, lat = coords[0], coords[1]
                name = props.get("name") or props.get("name_latin") or "Station"
                name_en = props.get("name_en")
                for cid, cinfo in city_boxes.items():
                    x0, y0, x1, y1 = cinfo["bbox"]
                    if x0 <= lon <= x1 and y0 <= lat <= y1:
                        city_stations[cid].append({
                            "type": "Feature",
                            "properties": {
                                "id": props.get("id"),
                                "name": name,
                                "name_en": name_en,
                                "city_id": cid
                            },
                            "geometry": geom
                        })

            elif rw == "rail":
                if gtype == "LineString":
                    all_pts = coords
                elif gtype == "MultiLineString":
                    all_pts = [p for seg in coords for p in seg]
                else:
                    continue

                lons = [p[0] for p in all_pts]
                lats = [p[1] for p in all_pts]
                min_x, max_x = min(lons), max(lons)
                min_y, max_y = min(lats), max(lats)

                name = props.get("name") or ""
                name_en = props.get("name_en") or props.get("name_latin") or ""

                is_hsr = any(p in name for p in hsr_patterns) or any(p in name_en.lower() for p in hsr_en_patterns)

                clean_props = {
                    "id": props.get("id"),
                    "name": name if name else None,
                    "name_en": name_en if name_en else None,
                    "is_hsr": is_hsr,
                    "railway_type": "High-Speed Rail" if is_hsr else "Conventional Rail",
                    "layer": props.get("layer"),
                    "city_id": None
                }

                for cid, cinfo in city_boxes.items():
                    x0, y0, x1, y1 = cinfo["bbox"]
                    if not (max_x < x0 or min_x > x1 or max_y < y0 or min_y > y1):
                        p_copy = dict(clean_props)
                        p_copy["city_id"] = cid
                        city_rails[cid].append({
                            "type": "Feature",
                            "properties": p_copy,
                            "geometry": geom
                        })

    print(f"Finished parsing {feature_count:,} features.")

    os.makedirs("data/processed/city_rails", exist_ok=True)
    summaries = {}

    all_rail_features = []
    all_station_features = []

    for c in cities:
        cid = c["id"]
        rails = city_rails[cid]
        stations = city_stations[cid]

        hsr_count = sum(1 for r in rails if r["properties"]["is_hsr"])
        conv_count = len(rails) - hsr_count

        # Identify unique named corridors with smart ranking
        named_corridors_set = set(
            r["properties"]["name"] for r in rails if r["properties"]["name"]
        )

        def corridor_rank(name):
            if name.endswith("道"): return (5, name)
            if any(k in name for k in ["公司", "厂", "处", "局", "库", "基地", "油", "专用线", "储运"]): return (4, name)
            if any(k in name for k in ["联络线", "疏解线", "走行线", "渡线"]): return (3, name)
            if any(k in name for k in ["高铁", "客专", "高速", "城际"]): return (0, name)
            if any(k in name for k in ["铁路", "线", "干线"]): return (1, name)
            return (2, name)

        ranked_corridors = sorted(named_corridors_set, key=corridor_rank)

        # Deduplicate stations by name with smart ranking
        station_names_set = set()
        unique_stations = []
        for s in stations:
            s_name = s["properties"]["name"]
            if s_name and s_name not in station_names_set:
                station_names_set.add(s_name)
                unique_stations.append(s)

        def station_rank(name):
            if any(k in name for k in ["火车站", "火车北站", "火车南站", "火车东站", "火车西站", "高铁站", "客运站", "机场"]): return (0, name)
            if any(name.endswith(k) for k in ["东站", "西站", "南站", "北站", "新客站"]): return (1, name)
            if name.endswith("站"): return (2, name)
            return (3, name)

        ranked_stations = sorted(station_names_set, key=station_rank)

        summaries[cid] = {
            "city_id": cid,
            "total_rail_segments": len(rails),
            "hsr_segments": hsr_count,
            "conventional_segments": conv_count,
            "station_count": len(unique_stations),
            "major_corridors": ranked_corridors[:12],
            "key_stations": ranked_stations[:10]
        }

        # Per-city geojson files
        city_fc = {
            "type": "FeatureCollection",
            "features": rails + unique_stations
        }
        with open(f"data/processed/city_rails/{cid}.geojson", "w", encoding="utf-8") as f:
            json.dump(city_fc, f, ensure_ascii=False)

        all_rail_features.extend(rails)
        all_station_features.extend(unique_stations)

    # Master summary
    with open("data/processed/city_rail_summary.json", "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("Saved per-city GeoJSON in data/processed/city_rails/ and data/processed/city_rail_summary.json.")

    # Compile data/processed/city_rails.rds for high-speed loading in R
    print("Compiling data/processed/city_rails.rds...")
    r_code = """
suppressPackageStartupMessages({
  library(sf)
  library(jsonlite)
})
stats <- fromJSON('data/processed/city_growth_stats.json')
city_rails <- list()
for (i in seq_len(nrow(stats))) {
  cid <- stats$id[i]
  gj <- sprintf('data/processed/city_rails/%s.geojson', cid)
  if (file.exists(gj)) {
    layers <- tryCatch({
      obj <- st_read(gj, quiet = TRUE)
      rails <- obj[st_geometry_type(obj) %in% c('LINESTRING', 'MULTILINESTRING'), ]
      stations <- obj[st_geometry_type(obj) %in% c('POINT', 'MULTIPOINT'), ]
      list(rails = rails, stations = stations)
    }, error = function(e) NULL)
    city_rails[[cid]] <- layers
  }
}
saveRDS(city_rails, 'data/processed/city_rails.rds')
cat(sprintf('Successfully written data/processed/city_rails.rds (%d cities, %0.2f MB)\\n',
            length(city_rails), file.size('data/processed/city_rails.rds') / 1024 / 1024))
"""
    import subprocess
    subprocess.run(["Rscript", "-e", r_code], check=True)

if __name__ == "__main__":
    main()
