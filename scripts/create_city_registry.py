import json, os, csv

# 47 cities exact metadata: English, Chinese, Pinyin, Province, Region, Center Lat, Center Lon, Approx Urban Radius km
CITIES_DATA = [
    {
        "id": "baicheng",
        "name_en": "Baicheng",
        "name_zh": "白城市",
        "pinyin": "Báichéng",
        "province_en": "Jilin",
        "province_zh": "吉林省",
        "region": "Northeast Rust Belt",
        "lat": 45.6190,
        "lon": 122.8410,
        "radius_km": 15,
        "gadm_name": "Baicheng"
    },
    {
        "id": "baoding",
        "name_en": "Baoding",
        "name_zh": "保定市",
        "pinyin": "Bǎodìng",
        "province_en": "Hebei",
        "province_zh": "河北省",
        "region": "Yellow River & North Plain",
        "lat": 38.8671,
        "lon": 115.4845,
        "radius_km": 20,
        "gadm_name": "Baoding"
    },
    {
        "id": "binzhou",
        "name_en": "Binzhou",
        "name_zh": "滨州市",
        "pinyin": "Bīnzhōu",
        "province_en": "Shandong",
        "province_zh": "山东省",
        "region": "Yellow River & North Plain",
        "lat": 37.3835,
        "lon": 118.0160,
        "radius_km": 18,
        "gadm_name": "Binzhou"
    },
    {
        "id": "chengdu",
        "name_en": "Chengdu",
        "name_zh": "成都市",
        "pinyin": "Chéngdū",
        "province_en": "Sichuan",
        "province_zh": "四川省",
        "region": "Yangtze Basin & Central",
        "lat": 30.6586,
        "lon": 104.0648,
        "radius_km": 30,
        "gadm_name": "Chengdu"
    },
    {
        "id": "dandong",
        "name_en": "Dandong",
        "name_zh": "丹东市",
        "pinyin": "Dāndōng",
        "province_en": "Liaoning",
        "province_zh": "辽宁省",
        "region": "Northeast Rust Belt",
        "lat": 40.1299,
        "lon": 124.3947,
        "radius_km": 18,
        "gadm_name": "Dandong"
    },
    {
        "id": "datong",
        "name_en": "Datong",
        "name_zh": "大同市",
        "pinyin": "Dàtóng",
        "province_en": "Shanxi",
        "province_zh": "山西省",
        "region": "Yellow River & North Plain",
        "lat": 40.0768,
        "lon": 113.3001,
        "radius_km": 18,
        "gadm_name": "Datong"
    },
    {
        "id": "dongying",
        "name_en": "Dongying",
        "name_zh": "东营市",
        "pinyin": "Dōngyíng",
        "province_en": "Shandong",
        "province_zh": "山东省",
        "region": "Yellow River & North Plain",
        "lat": 37.4338,
        "lon": 118.6747,
        "radius_km": 20,
        "gadm_name": "Dongying"
    },
    {
        "id": "fuxin",
        "name_en": "Fuxin",
        "name_zh": "阜新市",
        "pinyin": "Fùxīn",
        "province_en": "Liaoning",
        "province_zh": "辽宁省",
        "region": "Northeast Rust Belt",
        "lat": 42.0216,
        "lon": 121.6704,
        "radius_km": 16,
        "gadm_name": "Fuxin"
    },
    {
        "id": "guilin",
        "name_en": "Guilin",
        "name_zh": "桂林市",
        "pinyin": "Guìlín",
        "province_en": "Guangxi",
        "province_zh": "广西壮族自治区",
        "region": "South & Southwest",
        "lat": 25.2736,
        "lon": 110.2902,
        "radius_km": 18,
        "gadm_name": "Guilin"
    },
    {
        "id": "haikou",
        "name_en": "Haikou",
        "name_zh": "海口市",
        "pinyin": "Hǎikǒu",
        "province_en": "Hainan",
        "province_zh": "海南省",
        "region": "Pearl River & South Coast",
        "lat": 20.0440,
        "lon": 110.3293,
        "radius_km": 20,
        "gadm_name": "Haikou"
    },
    {
        "id": "harbin",
        "name_en": "Harbin",
        "name_zh": "哈尔滨市",
        "pinyin": "Hā'ěrbīn",
        "province_en": "Heilongjiang",
        "province_zh": "黑龙江省",
        "region": "Northeast Rust Belt",
        "lat": 45.8038,
        "lon": 126.5349,
        "radius_km": 28,
        "gadm_name": "Harbin"
    },
    {
        "id": "heyuan",
        "name_en": "Heyuan",
        "name_zh": "河源市",
        "pinyin": "Héyuán",
        "province_en": "Guangdong",
        "province_zh": "广东省",
        "region": "Pearl River & South Coast",
        "lat": 23.7438,
        "lon": 114.6978,
        "radius_km": 16,
        "gadm_name": "Heyuan"
    },
    {
        "id": "hohhot",
        "name_en": "Hohhot",
        "name_zh": "呼和浩特市",
        "pinyin": "Hūhéhàotè",
        "province_en": "Inner Mongolia",
        "province_zh": "内蒙古自治区",
        "region": "Western Frontier & Steppe",
        "lat": 40.8415,
        "lon": 111.7519,
        "radius_km": 20,
        "gadm_name": "Hohhot"
    },
    {
        "id": "hotan",
        "name_en": "Hotan",
        "name_zh": "和田市",
        "pinyin": "Hétián",
        "province_en": "Xinjiang",
        "province_zh": "新疆维吾尔自治区",
        "region": "Western Frontier & Steppe",
        "lat": 37.1107,
        "lon": 79.9135,
        "radius_km": 14,
        "gadm_name": "Khotan"
    },
    {
        "id": "huangshan",
        "name_en": "Huangshan",
        "name_zh": "黄山市",
        "pinyin": "Huángshān",
        "province_en": "Anhui",
        "province_zh": "安徽省",
        "region": "Yangtze Delta & East",
        "lat": 29.7147,
        "lon": 118.3375,
        "radius_km": 15,
        "gadm_name": "Huangshan"
    },
    {
        "id": "hunchun",
        "name_en": "Hunchun",
        "name_zh": "珲春市",
        "pinyin": "Húnchūn",
        "province_en": "Jilin",
        "province_zh": "吉林省",
        "region": "Northeast Rust Belt",
        "lat": 42.8628,
        "lon": 130.3653,
        "radius_km": 12,
        "gadm_name": "YanbianKorean"
    },
    {
        "id": "jinan",
        "name_en": "Jinan",
        "name_zh": "济南市",
        "pinyin": "Jǐnán",
        "province_en": "Shandong",
        "province_zh": "山东省",
        "region": "Yellow River & North Plain",
        "lat": 36.6512,
        "lon": 117.1201,
        "radius_km": 25,
        "gadm_name": "Jinan"
    },
    {
        "id": "jining",
        "name_en": "Jining",
        "name_zh": "济宁市",
        "pinyin": "Jǐnìng",
        "province_en": "Shandong",
        "province_zh": "山东省",
        "region": "Yellow River & North Plain",
        "lat": 35.4154,
        "lon": 116.5872,
        "radius_km": 20,
        "gadm_name": "Jining"
    },
    {
        "id": "kashgar",
        "name_en": "Kashgar",
        "name_zh": "喀什市",
        "pinyin": "Kāshí",
        "province_en": "Xinjiang",
        "province_zh": "新疆维吾尔自治区",
        "region": "Western Frontier & Steppe",
        "lat": 39.4704,
        "lon": 75.9897,
        "radius_km": 16,
        "gadm_name": "Kashgar"
    },
    {
        "id": "korla",
        "name_en": "Korla",
        "name_zh": "库尔勒市",
        "pinyin": "Kù'ěrlè",
        "province_en": "Xinjiang",
        "province_zh": "新疆维吾尔自治区",
        "region": "Western Frontier & Steppe",
        "lat": 41.7259,
        "lon": 86.1746,
        "radius_km": 16,
        "gadm_name": "Bayin'gholinMongol"
    },
    {
        "id": "kunming",
        "name_en": "Kunming",
        "name_zh": "昆明市",
        "pinyin": "Kūnmíng",
        "province_en": "Yunnan",
        "province_zh": "云南省",
        "region": "South & Southwest",
        "lat": 24.8797,
        "lon": 102.8332,
        "radius_km": 25,
        "gadm_name": "Kunming"
    },
    {
        "id": "lanzhou",
        "name_en": "Lanzhou",
        "name_zh": "兰州市",
        "pinyin": "Lánzhōu",
        "province_en": "Gansu",
        "province_zh": "甘肃省",
        "region": "Western Frontier & Steppe",
        "lat": 36.0611,
        "lon": 103.8343,
        "radius_km": 22,
        "gadm_name": "Lanzhou"
    },
    {
        "id": "lianyungang",
        "name_en": "Lianyungang",
        "name_zh": "连云港市",
        "pinyin": "Liányúngǎng",
        "province_en": "Jiangsu",
        "province_zh": "江苏省",
        "region": "Yangtze Delta & East",
        "lat": 34.5967,
        "lon": 119.2216,
        "radius_km": 22,
        "gadm_name": "Lianyungang"
    },
    {
        "id": "liaocheng",
        "name_en": "Liaocheng",
        "name_zh": "聊城市",
        "pinyin": "Liáochéng",
        "province_en": "Shandong",
        "province_zh": "山东省",
        "region": "Yellow River & North Plain",
        "lat": 36.4570,
        "lon": 115.9854,
        "radius_km": 18,
        "gadm_name": "Liaocheng"
    },
    {
        "id": "liaoyuan",
        "name_en": "Liaoyuan",
        "name_zh": "辽源市",
        "pinyin": "Liáoyuán",
        "province_en": "Jilin",
        "province_zh": "吉林省",
        "region": "Northeast Rust Belt",
        "lat": 42.9027,
        "lon": 125.1432,
        "radius_km": 15,
        "gadm_name": "Liaoyuan"
    },
    {
        "id": "luzhou",
        "name_en": "Luzhou",
        "name_zh": "泸州市",
        "pinyin": "Lúzhōu",
        "province_en": "Sichuan",
        "province_zh": "四川省",
        "region": "Yangtze Basin & Central",
        "lat": 28.8719,
        "lon": 105.4423,
        "radius_km": 18,
        "gadm_name": "Luzhou"
    },
    {
        "id": "nanchang",
        "name_en": "Nanchang",
        "name_zh": "南昌市",
        "pinyin": "Nánchāng",
        "province_en": "Jiangxi",
        "province_zh": "江西省",
        "region": "Yangtze Basin & Central",
        "lat": 28.6829,
        "lon": 115.8582,
        "radius_km": 24,
        "gadm_name": "Nanchang"
    },
    {
        "id": "panjin",
        "name_en": "Panjin",
        "name_zh": "盘锦市",
        "pinyin": "Pánjǐn",
        "province_en": "Liaoning",
        "province_zh": "辽宁省",
        "region": "Northeast Rust Belt",
        "lat": 41.1244,
        "lon": 122.0707,
        "radius_km": 18,
        "gadm_name": "Panjin"
    },
    {
        "id": "shenzhen",
        "name_en": "Shenzhen",
        "name_zh": "深圳市",
        "pinyin": "Shēnzhèn",
        "province_en": "Guangdong",
        "province_zh": "广东省",
        "region": "Pearl River & South Coast",
        "lat": 22.5431,
        "lon": 114.0579,
        "radius_km": 28,
        "gadm_name": "Shenzhen"
    },
    {
        "id": "shijiazhuang",
        "name_en": "Shijiazhuang",
        "name_zh": "石家庄市",
        "pinyin": "Shíjiāzhuāng",
        "province_en": "Hebei",
        "province_zh": "河北省",
        "region": "Yellow River & North Plain",
        "lat": 38.0428,
        "lon": 114.5149,
        "radius_km": 25,
        "gadm_name": "Shijiazhuang"
    },
    {
        "id": "taishan",
        "name_en": "Taishan",
        "name_zh": "台山市",
        "pinyin": "Táishān",
        "province_en": "Guangdong",
        "province_zh": "广东省",
        "region": "Pearl River & South Coast",
        "lat": 22.2514,
        "lon": 112.7938,
        "radius_km": 15,
        "gadm_name": "Jiangmen"
    },
    {
        "id": "taizhou",
        "name_en": "Taizhou",
        "name_zh": "泰州市",
        "pinyin": "Tàizhōu",
        "province_en": "Jiangsu",
        "province_zh": "江苏省",
        "region": "Yangtze Delta & East",
        "lat": 32.4555,
        "lon": 119.9229,
        "radius_km": 20,
        "gadm_name": "Taizhou"
    },
    {
        "id": "tieling",
        "name_en": "Tieling",
        "name_zh": "铁岭市",
        "pinyin": "Tiělǐng",
        "province_en": "Liaoning",
        "province_zh": "辽宁省",
        "region": "Northeast Rust Belt",
        "lat": 42.2907,
        "lon": 123.8443,
        "radius_km": 16,
        "gadm_name": "Tieling"
    },
    {
        "id": "ulanqab",
        "name_en": "Ulanqab",
        "name_zh": "乌兰察布市",
        "pinyin": "Wūlánchábù",
        "province_en": "Inner Mongolia",
        "province_zh": "内蒙古自治区",
        "region": "Western Frontier & Steppe",
        "lat": 41.0180,
        "lon": 113.1326,
        "radius_km": 16,
        "gadm_name": "UlaanChab"
    },
    {
        "id": "urumqi",
        "name_en": "Urumqi",
        "name_zh": "乌鲁木齐市",
        "pinyin": "Wūlǔmùqí",
        "province_en": "Xinjiang",
        "province_zh": "新疆维吾尔自治区",
        "region": "Western Frontier & Steppe",
        "lat": 43.8256,
        "lon": 87.6168,
        "radius_km": 26,
        "gadm_name": "Ürümqi"
    },
    {
        "id": "weihai",
        "name_en": "Weihai",
        "name_zh": "威海市",
        "pinyin": "Wēihǎi",
        "province_en": "Shandong",
        "province_zh": "山东省",
        "region": "Yellow River & North Plain",
        "lat": 37.5131,
        "lon": 122.1205,
        "radius_km": 20,
        "gadm_name": "Weihai"
    },
    {
        "id": "wuhan",
        "name_en": "Wuhan",
        "name_zh": "武汉市",
        "pinyin": "Wǔhàn",
        "province_en": "Hubei",
        "province_zh": "湖北省",
        "region": "Yangtze Basin & Central",
        "lat": 30.5928,
        "lon": 114.3055,
        "radius_km": 30,
        "gadm_name": "Wuhan"
    },
    {
        "id": "wuhu",
        "name_en": "Wuhu",
        "name_zh": "芜湖市",
        "pinyin": "Wúhú",
        "province_en": "Anhui",
        "province_zh": "安徽省",
        "region": "Yangtze Delta & East",
        "lat": 31.3528,
        "lon": 118.3765,
        "radius_km": 20,
        "gadm_name": "Wuhu"
    },
    {
        "id": "wuwei",
        "name_en": "Wuwei",
        "name_zh": "武威市",
        "pinyin": "Wǔwēi",
        "province_en": "Gansu",
        "province_zh": "甘肃省",
        "region": "Western Frontier & Steppe",
        "lat": 37.9283,
        "lon": 102.6379,
        "radius_km": 16,
        "gadm_name": "Wuwei"
    },
    {
        "id": "xiamen",
        "name_en": "Xiamen",
        "name_zh": "厦门市",
        "pinyin": "Xiàmén",
        "province_en": "Fujian",
        "province_zh": "福建省",
        "region": "Pearl River & South Coast",
        "lat": 24.4798,
        "lon": 118.0894,
        "radius_km": 22,
        "gadm_name": "Xiamen"
    },
    {
        "id": "xian",
        "name_en": "Xi'an",
        "name_zh": "西安市",
        "pinyin": "Xī'ān",
        "province_en": "Shaanxi",
        "province_zh": "陕西省",
        "region": "Western Frontier & Steppe",
        "lat": 34.3416,
        "lon": 108.9398,
        "radius_km": 28,
        "gadm_name": "Xi'an"
    },
    {
        "id": "yangzhou",
        "name_en": "Yangzhou",
        "name_zh": "扬州市",
        "pinyin": "Yángzhōu",
        "province_en": "Jiangsu",
        "province_zh": "江苏省",
        "region": "Yangtze Delta & East",
        "lat": 32.3942,
        "lon": 119.4129,
        "radius_km": 20,
        "gadm_name": "Yangzhou"
    },
    {
        "id": "yichang",
        "name_en": "Yichang",
        "name_zh": "宜昌市",
        "pinyin": "Yíchāng",
        "province_en": "Hubei",
        "province_zh": "湖北省",
        "region": "Yangtze Basin & Central",
        "lat": 30.6919,
        "lon": 111.2865,
        "radius_km": 20,
        "gadm_name": "Yichang"
    },
    {
        "id": "zhangjiajie",
        "name_en": "Zhangjiajie",
        "name_zh": "张家界市",
        "pinyin": "Zhāngjiājiè",
        "province_en": "Hunan",
        "province_zh": "湖南省",
        "region": "Yangtze Basin & Central",
        "lat": 29.1170,
        "lon": 110.4792,
        "radius_km": 16,
        "gadm_name": "Zhangjiajie"
    },
    {
        "id": "zhengzhou",
        "name_en": "Zhengzhou",
        "name_zh": "郑州市",
        "pinyin": "Zhèngzhōu",
        "province_en": "Henan",
        "province_zh": "河南省",
        "region": "Yellow River & North Plain",
        "lat": 34.7466,
        "lon": 113.6253,
        "radius_km": 28,
        "gadm_name": "Zhengzhou"
    },
    {
        "id": "zhuhai",
        "name_en": "Zhuhai",
        "name_zh": "珠海市",
        "pinyin": "Zhūhǎi",
        "province_en": "Guangdong",
        "province_zh": "广东省",
        "region": "Pearl River & South Coast",
        "lat": 22.2707,
        "lon": 113.5767,
        "radius_km": 22,
        "gadm_name": "Zhuhai"
    },
    {
        "id": "zibo",
        "name_en": "Zibo",
        "name_zh": "淄博市",
        "pinyin": "Zībó",
        "province_en": "Shandong",
        "province_zh": "山东省",
        "region": "Yellow River & North Plain",
        "lat": 36.8135,
        "lon": 118.0549,
        "radius_km": 22,
        "gadm_name": "Zibo"
    }
]

# Calculate bbox (in WGS84 degrees) and required WSF tiles
import math
for c in CITIES_DATA:
    lat = c["lat"]
    lon = c["lon"]
    rad_km = c["radius_km"]
    
    # 1 deg lat ~ 111 km
    dlat = rad_km / 111.0
    # 1 deg lon ~ 111 * cos(lat) km
    dlon = rad_km / (111.0 * math.cos(math.radians(lat)))
    
    c["bbox"] = [
        round(lon - dlon, 4),
        round(lat - dlat, 4),
        round(lon + dlon, 4),
        round(lat + dlat, 4)
    ]
    
    # WSF tiles needed: 2x2 deg grid
    # Tile origin: even integer <= lon, even integer <= lat
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
with open("data/cities.json", "w", encoding="utf-8") as f:
    json.dump(CITIES_DATA, f, ensure_ascii=False, indent=2)

with open("data/cities.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "id", "name_en", "name_zh", "pinyin", "province_en", "province_zh",
        "region", "lat", "lon", "radius_km", "bbox", "wsf_tiles"
    ])
    writer.writeheader()
    for row in CITIES_DATA:
        r = dict(row)
        r["bbox"] = ",".join(map(str, r["bbox"]))
        r["wsf_tiles"] = ";".join(r["wsf_tiles"])
        del r["gadm_name"]
        writer.writerow(r)

print(f"Written data/cities.json and data/cities.csv ({len(CITIES_DATA)} cities).")
