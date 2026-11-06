import urllib.request, re, json, math, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROC_DIR = ROOT / "data" / "processed"
SUBWAY_DIR = PROC_DIR / "city_subways"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROC_DIR.mkdir(parents=True, exist_ok=True)
SUBWAY_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. Coordinate Conversion Helper: GCJ-02 (Amap) -> WGS-84 (Standard GPS / WSF)
# -----------------------------------------------------------------------------
def gcj02_to_wgs84(lng, lat):
    a = 6378245.0
    ee = 0.00669342162296594323
    if not (73.66 < lng < 135.05 and 3.86 < lat < 53.55):
        return lng, lat
    
    def transformlat(lng, lat):
        ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(abs(lng))
        ret += (20.0 * math.sin(6.0 * lng * math.pi) + 20.0 * math.sin(2.0 * lng * math.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lat * math.pi) + 40.0 * math.sin(lat / 3.0 * math.pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(lat / 12.0 * math.pi) + 320 * math.sin(lat * math.pi / 30.0)) * 2.0 / 3.0
        return ret

    def transformlng(lng, lat):
        ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(abs(lng))
        ret += (20.0 * math.sin(6.0 * lng * math.pi) + 20.0 * math.sin(2.0 * lng * math.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lng * math.pi) + 40.0 * math.sin(lng / 3.0 * math.pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(lng / 12.0 * math.pi) + 300.0 * math.sin(lng / 30.0 * math.pi)) * 2.0 / 3.0
        return ret

    dlat = transformlat(lng - 105.0, lat - 35.0)
    dlng = transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * math.pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * math.pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * math.pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return round(lng * 2 - mglng, 6), round(lat * 2 - mglat, 6)

# -----------------------------------------------------------------------------
# 2. Fetch National China Railway Dataset (12306 Passenger Rail Network)
# -----------------------------------------------------------------------------
print("Fetching authentic China National Passenger Railway Network (12306 / NRA)...")
url_rail = "https://raw.githubusercontent.com/saikewei/rail-map-cn/main/map.html"
req_rail = urllib.request.Request(url_rail, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req_rail, timeout=60) as resp:
    html = resp.read().decode("utf-8")

match = re.search(r'window\.ATLAS\s*=\s*(\{.*?\});\s*window\.GLYPHS', html, re.DOTALL)
if not match:
    raise ValueError("Could not extract ATLAS from saikewei/rail-map-cn map.html")

atlas_data = json.loads(match.group(1))
lines_list = atlas_data["lines"]
stations_list = atlas_data["stations"]
rail_geojson = atlas_data["rail"]

print(f"Loaded {len(lines_list)} passenger rail lines, {len(stations_list)} stations, {len(rail_geojson['features'])} geometry features.")

# Save raw national rail GeoJSON and station points
with open(RAW_DIR / "china_railway_12306_lines.geojson", "w", encoding="utf-8") as f:
    json.dump(rail_geojson, f, ensure_ascii=False)

# Convert stations to GeoJSON FeatureCollection
station_features = []
for s in stations_list:
    station_features.append({
        "type": "Feature",
        "properties": {
            "id": s.get("id"),
            "name": s.get("name"),
            "city": s.get("city"),
            "province": s.get("province"),
            "telecode": s.get("tele"),
            "pinyin": s.get("py"),
            "tier": s.get("tier"),
            "rank": s.get("rank"),
            "lines": [l.get("name") for l in s.get("lines", [])]
        },
        "geometry": {
            "type": "Point",
            "coordinates": [round(s["lon"], 6), round(s["lat"], 6)]
        }
    })

stations_geojson = {
    "type": "FeatureCollection",
    "features": station_features
}
with open(RAW_DIR / "china_railway_12306_stations.geojson", "w", encoding="utf-8") as f:
    json.dump(stations_geojson, f, ensure_ascii=False)

# Save line metadata lookup
with open(RAW_DIR / "china_railway_12306_line_metadata.json", "w", encoding="utf-8") as f:
    json.dump(lines_list, f, ensure_ascii=False, indent=2)

print("Saved National Railway GeoJSONs to data/raw/.")

# -----------------------------------------------------------------------------
# 3. Fetch Official City Subway Networks from AMap (高德地图地铁服务)
# -----------------------------------------------------------------------------
subway_city_codes = {
    'chengdu': ('5101', 'chengdu', '成都市'),
    'shenzhen': ('4403', 'shenzhen', '深圳市'),
    'xian': ('6101', 'xian', '西安市'),
    'zhengzhou': ('4101', 'zhengzhou', '郑州市'),
    'wuhan': ('4201', 'wuhan', '武汉市'),
    'shijiazhuang': ('1301', 'shijiazhuang', '石家庄市'),
    'harbin': ('2301', 'haerbin', '哈尔滨市'),
    'jinan': ('3701', 'jinan', '济南市'),
    'kunming': ('5301', 'kunming', '昆明市'),
    'nanchang': ('3601', 'nanchang', '南昌市'),
    'xiamen': ('3502', 'xiamen', '厦门市'),
    'lanzhou': ('6201', 'lanzhou', '兰州市'),
    'urumqi': ('6501', 'wulumuqi', '乌鲁木齐市'),
    'wuhu': ('3402', 'wuhu', '芜湖市'),
    'hohhot': ('1501', 'huhehaote', '呼和浩特市')
}

subway_summary = {}

for cid, (code, spell, cname) in subway_city_codes.items():
    print(f"Fetching subway network for {cid} ({cname})...")
    url_sub = f"http://map.amap.com/service/subway?_r=0.123&srhdata={code}_drw_{spell}.json"
    req_sub = urllib.request.Request(url_sub, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req_sub, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Failed to fetch subway for {cid}: {e}")
        continue
    
    line_features = []
    station_features = []
    seen_stations = set()
    line_names_list = []
    
    for l in data.get('l', []):
        line_name = l.get('kn', '')
        short_name = l.get('ln', '')
        line_key = line_name or short_name
        color = f"#{l.get('cl', '38BDF8')}"
        if line_key and line_key not in line_names_list:
            line_names_list.append(line_key)
            
        line_coords = []
        for s in l.get('st', []):
            st_name = s.get('n', '')
            sl = s.get('sl', '')
            if not sl:
                continue
            gcj_lng, gcj_lat = [float(x) for x in sl.split(',')]
            wgs_lng, wgs_lat = gcj02_to_wgs84(gcj_lng, gcj_lat)
            line_coords.append([wgs_lng, wgs_lat])
            
            if st_name not in seen_stations:
                seen_stations.add(st_name)
                station_features.append({
                    "type": "Feature",
                    "properties": {
                        "name": st_name,
                        "line_name": line_name,
                        "short_name": short_name,
                        "color": color,
                        "city_id": cid
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [wgs_lng, wgs_lat]
                    }
                })
        if len(line_coords) >= 2:
            line_features.append({
                "type": "Feature",
                "properties": {
                    "name": line_name,
                    "short_name": short_name,
                    "color": color,
                    "station_count": len(line_coords),
                    "city_id": cid
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": line_coords
                }
            })
            
    # Save city subway GeoJSON
    subway_geojson = {
        "type": "FeatureCollection",
        "city_id": cid,
        "city_name": cname,
        "features": line_features + station_features
    }
    with open(SUBWAY_DIR / f"{cid}_subway.geojson", "w", encoding="utf-8") as f:
        json.dump(subway_geojson, f, ensure_ascii=False)
        
    subway_summary[cid] = {
        "has_subway": True,
        "city_id": cid,
        "city_name": cname,
        "lines_count": len(line_names_list),
        "total_stations": len(seen_stations),
        "line_names": line_names_list[:12],
        "key_stations": [s["properties"]["name"] for s in station_features[:10]],
        "source": "AMap (高德地图) Subway Platform"
    }
    print(f"  ✓ {cid}: {len(line_names_list)} lines, {len(seen_stations)} stations saved.")

# Save master subway summary
with open(PROC_DIR / "city_subway_summary.json", "w", encoding="utf-8") as f:
    json.dump(subway_summary, f, ensure_ascii=False, indent=2)

print(f"Successfully processed subways for {len(subway_summary)} cities.")
