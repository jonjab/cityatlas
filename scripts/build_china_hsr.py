import json, os

# Curated High-Speed Rail (HSR) Network connecting China's urban hierarchy
# Coordinates represent key waypoints along each primary HSR corridor.

HSR_CORRIDORS = [
    {
        "name": "Beijing–Hong Kong Corridor (京港高铁)",
        "name_zh": "京港通道",
        "speed": "350 km/h",
        "coords": [
            [116.4074, 39.9042], # Beijing
            [115.4845, 38.8671], # Baoding
            [114.5149, 38.0428], # Shijiazhuang
            [114.4906, 36.6123], # Handan
            [113.6253, 34.7466], # Zhengzhou
            [114.3055, 30.5928], # Wuhan
            [112.9388, 28.2282], # Changsha
            [113.2644, 23.1291], # Guangzhou
            [114.0579, 22.5431], # Shenzhen
            [114.1694, 22.3193]  # Hong Kong (West Kowloon)
        ]
    },
    {
        "name": "Beijing–Shanghai Corridor (京沪高铁)",
        "name_zh": "京沪通道",
        "speed": "350 km/h",
        "coords": [
            [116.4074, 39.9042], # Beijing
            [117.2008, 39.0842], # Tianjin
            [116.8388, 37.4354], # Dezhou
            [117.1201, 36.6512], # Jinan
            [117.1848, 36.1954], # Tai'an
            [116.9845, 34.2610], # Xuzhou
            [117.3897, 32.9163], # Bengbu
            [118.7969, 32.0603], # Nanjing
            [119.4129, 32.3942], # Yangzhou
            [119.9229, 32.4555], # Taizhou
            [120.5853, 31.2990], # Suzhou
            [121.4737, 31.2304]  # Shanghai
        ]
    },
    {
        "name": "Eurasian Landbridge / Lanxin HSR (陇海·兰新高铁)",
        "name_zh": "陆桥通道 / 兰新客专",
        "speed": "250-350 km/h",
        "coords": [
            [119.2216, 34.5967], # Lianyungang
            [116.9845, 34.2610], # Xuzhou
            [115.6563, 34.4140], # Shangqiu
            [113.6253, 34.7466], # Zhengzhou
            [112.4539, 34.6197], # Luoyang
            [108.9398, 34.3416], # Xi'an
            [107.2375, 34.3619], # Baoji
            [105.7249, 34.5809], # Tianshui
            [103.8343, 36.0611], # Lanzhou
            [101.7782, 36.6232], # Xining
            [102.6379, 37.9283], # Wuwei (Lanzhou-Xinjiang artery)
            [100.4498, 38.9259], # Zhangye
            [98.2892, 39.7731],  # Jiayuguan
            [93.5152, 42.8185],  # Hami
            [89.1897, 42.9513],  # Turpan
            [87.6168, 43.8256]   # Urumqi
        ]
    },
    {
        "name": "Yangtze River Corridor (沿江通道 / 沪汉蓉高铁)",
        "name_zh": "沿江通道",
        "speed": "250-350 km/h",
        "coords": [
            [121.4737, 31.2304], # Shanghai
            [120.5853, 31.2990], # Suzhou
            [118.7969, 32.0603], # Nanjing
            [118.3765, 31.3528], # Wuhu
            [117.2272, 31.8206], # Hefei
            [114.3055, 30.5928], # Wuhan
            [112.1866, 30.3352], # Jingzhou
            [111.2865, 30.6919], # Yichang
            [109.4869, 30.2875], # Enshi
            [106.5516, 29.5630], # Chongqing
            [105.4423, 28.8719], # Luzhou
            [104.0648, 30.6586]  # Chengdu
        ]
    },
    {
        "name": "Shanghai–Kunming Corridor (沪昆高铁)",
        "name_zh": "沪昆通道",
        "speed": "350 km/h",
        "coords": [
            [121.4737, 31.2304], # Shanghai
            [120.1551, 30.2741], # Hangzhou
            [118.8758, 28.9701], # Quzhou
            [117.9654, 28.4532], # Shangrao
            [115.8582, 28.6829], # Nanchang
            [113.8522, 27.6229], # Pingxiang
            [112.9388, 28.2282], # Changsha
            [111.6069, 27.2389], # Shaoyang
            [109.9985, 27.5550], # Huaihua
            [106.7135, 26.5783], # Guiyang
            [104.8955, 25.0921], # Anshun
            [102.8332, 24.8797]  # Kunming
        ]
    },
    {
        "name": "Xi'an–Chengdu High-Speed Railway (西成高铁)",
        "name_zh": "西成客专",
        "speed": "250 km/h",
        "coords": [
            [108.9398, 34.3416], # Xi'an
            [107.0319, 33.0677], # Hanzhong
            [105.8434, 32.4355], # Guangyuan
            [104.7417, 31.4640], # Mianyang
            [104.3986, 31.1270], # Deyang
            [104.0648, 30.6586]  # Chengdu
        ]
    },
    {
        "name": "Coastal Corridor (沿海高铁通道)",
        "name_zh": "沿海通道",
        "speed": "250-350 km/h",
        "coords": [
            [124.3947, 40.1299], # Dandong
            [121.6147, 38.9140], # Dalian
            [121.4479, 37.4638], # Yantai
            [122.1205, 37.5131], # Weihai
            [120.3826, 36.0671], # Qingdao
            [119.4612, 35.4285], # Rizhao
            [119.2216, 34.5967], # Lianyungang
            [120.1636, 33.3474], # Yancheng
            [120.8943, 31.9802], # Nantong
            [121.4737, 31.2304], # Shanghai
            [120.1551, 30.2741], # Hangzhou
            [121.5440, 29.8683], # Ningbo
            [120.6994, 27.9943], # Wenzhou
            [119.3062, 26.0753], # Fuzhou
            [118.0894, 24.4798], # Xiamen
            [116.6820, 23.3541], # Shantou
            [114.6978, 23.7438], # Heyuan / Coastal interior
            [114.0579, 22.5431], # Shenzhen
            [113.5767, 22.2707], # Zhuhai
            [112.7938, 22.2514]  # Taishan / Jiangmen
        ]
    },
    {
        "name": "Beijing–Harbin Corridor (京哈客专)",
        "name_zh": "京哈通道",
        "speed": "350 km/h",
        "coords": [
            [116.4074, 39.9042], # Beijing
            [119.6005, 39.9354], # Qinhuangdao
            [120.8569, 40.7111], # Huludao
            [121.1270, 41.0951], # Jinzhou
            [122.0707, 41.1244], # Panjin
            [123.4315, 41.8057], # Shenyang
            [123.8443, 42.2907], # Tieling
            [125.1432, 42.9027], # Liaoyuan / Siping
            [125.3235, 43.8171], # Changchun
            [126.5349, 45.8038]  # Harbin
        ]
    },
    {
        "name": "Northeast Border Link / Changhui HSR (长珲城际铁路)",
        "name_zh": "长珲城际",
        "speed": "250 km/h",
        "coords": [
            [125.3235, 43.8171], # Changchun
            [126.5645, 43.8379], # Jilin City
            [129.5132, 42.9068], # Yanji
            [130.3653, 42.8628]  # Hunchun
        ]
    },
    {
        "name": "Hohhot–Nanning Corridor (呼南高铁)",
        "name_zh": "呼南通道",
        "speed": "250-350 km/h",
        "coords": [
            [111.7519, 40.8415], # Hohhot
            [113.1326, 41.0180], # Ulanqab
            [113.3001, 40.0768], # Datong
            [112.5489, 37.8706], # Taiyuan
            [113.1235, 36.1954], # Changzhi
            [112.8654, 35.4912], # Jincheng
            [113.2382, 35.2389], # Jiaozuo
            [113.6253, 34.7466], # Zhengzhou
            [112.5283, 33.0044], # Nanyang
            [112.1441, 32.0424], # Xiangyang
            [111.2865, 30.6919], # Yichang
            [110.4792, 29.1170], # Zhangjiajie
            [110.2902, 25.2736], # Guilin
            [109.4286, 24.3260], # Liuzhou
            [108.3661, 22.8172]  # Nanning
        ]
    },
    {
        "name": "Qingdao–Yinchuan / Jiaoji Corridor (青银·胶济高铁)",
        "name_zh": "青银通道",
        "speed": "250-350 km/h",
        "coords": [
            [114.5149, 38.0428], # Shijiazhuang
            [115.9854, 36.4570], # Liaocheng (Jinan link)
            [117.1201, 36.6512], # Jinan
            [118.0549, 36.8135], # Zibo
            [118.0160, 37.3835], # Binzhou
            [119.1618, 36.7068], # Weifang
            [120.3826, 36.0671], # Qingdao
            [122.1205, 37.5131]  # Weihai
        ]
    },
    {
        "name": "Hainan Island Ring High-Speed Railway (海南环岛高铁)",
        "name_zh": "海南环岛客专",
        "speed": "250 km/h",
        "coords": [
            [110.3293, 20.0440], # Haikou
            [110.7941, 19.6105], # Wenchang
            [110.4665, 19.2458], # Qionghai
            [110.0268, 18.7963], # Wanning
            [109.5119, 18.2528], # Sanya
            [108.6536, 19.1011], # Dongfang
            [109.5811, 19.5218], # Danzhou
            [110.3293, 20.0440]  # Haikou Loop
        ]
    },
    {
        "name": "Southern Xinjiang Silk Road Railway (南疆·和若铁路)",
        "name_zh": "南疆铁路",
        "speed": "160-200 km/h",
        "coords": [
            [87.6168, 43.8256],  # Urumqi
            [86.1746, 41.7259],  # Korla
            [82.8711, 41.7282],  # Kuqa
            [80.2634, 41.1688],  # Aksu
            [75.9897, 39.4704],  # Kashgar
            [77.2662, 38.4168],  # Yarkant
            [79.9135, 37.1107]   # Hotan
        ]
    }
]

features = []
for h in HSR_CORRIDORS:
    features.append({
        "type": "Feature",
        "properties": {
            "name": h["name"],
            "name_zh": h["name_zh"],
            "speed": h["speed"],
            "type": "High-Speed Rail"
        },
        "geometry": {
            "type": "LineString",
            "coordinates": h["coords"]
        }
    })

geojson = {
    "type": "FeatureCollection",
    "features": features
}

os.makedirs("data/processed", exist_ok=True)
with open("data/processed/china_hsr.geojson", "w", encoding="utf-8") as f:
    json.dump(geojson, f, indent=2, ensure_ascii=False)

print(f"Generated data/processed/china_hsr.geojson with {len(features)} primary HSR corridors!")
