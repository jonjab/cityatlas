import json, urllib.request, urllib.parse, time, os

def get_json(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "ChinaAtlasBot/1.0 (exploratory_urban_geography; contact@ucsb.edu)"
    })
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        # Retry once after a brief pause
        time.sleep(0.5)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
        except Exception as e2:
            print(f"Error fetching {url}: {e2}")
            return None

def main():
    print("Fetching Wikipedia, Wikidata & Commons resources for 47 cities...")
    with open("data/cities.json", "r", encoding="utf-8") as f:
        cities = json.load(f)

    # Disambiguation mapping for English Wikipedia
    en_disambig = {
        "taizhou": "Taizhou, Jiangsu",
        "wuwei": "Wuwei, Gansu",
        "huangshan": "Huangshan City",
        "taishan": "Taishan",
        "kashgar": "Kashgar",
        "korla": "Korla",
        "hotan": "Hotan",
        "hunchun": "Hunchun",
        "jining": "Jining",
        "panjin": "Panjin",
        "fuxin": "Fuxin",
        "liaoyuan": "Liaoyuan",
        "ulanqab": "Ulanqab"
    }

    # Disambiguation for Chinese Wikipedia if needed
    zh_disambig = {
        "taizhou": "泰州市",
        "wuwei": "武威市",
        "huangshan": "黄山市",
        "taishan": "台山市",
        "kashgar": "喀什市",
        "korla": "库尔勒市",
        "hotan": "和田市",
        "hunchun": "珲春市"
    }

    results = {}

    for c in cities:
        cid = c["id"]
        name_en = c["name_en"]
        name_zh = c["name_zh"]
        en_title = en_disambig.get(cid, name_en)

        print(f"Processing {name_en} ({cid})...")

        # 1. English Wikipedia & Wikidata QID
        en_query_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(en_title)}&prop=info|pageprops|langlinks&lllang=zh&inprop=url&format=json"
        en_data = get_json(en_query_url)

        qid = None
        en_url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(en_title)}"
        en_page_title = en_title
        zh_page_title = zh_disambig.get(cid, name_zh)

        if en_data and "query" in en_data and "pages" in en_data["query"]:
            page = list(en_data["query"]["pages"].values())[0]
            if "missing" not in page:
                qid = page.get("pageprops", {}).get("wikibase_item")
                en_url = page.get("fullurl", en_url)
                en_page_title = page.get("title", en_title)
                if "langlinks" in page and page["langlinks"]:
                    zh_page_title = page["langlinks"][0]["*"]

        zh_url = f"https://zh.wikipedia.org/wiki/{urllib.parse.quote(zh_page_title)}"
        wikidata_url = f"https://www.wikidata.org/wiki/{qid}" if qid else None

        # 2. Check Commons categories for maps
        test_cats = [
            f"Category:Maps of {name_en}",
            f"Category:Old maps of {name_en}",
            f"Category:Maps of {en_page_title}",
            f"Category:Maps of {name_zh}"
        ]
        cat_url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote('|'.join(test_cats))}&format=json"
        cat_data = get_json(cat_url)

        found_cats = []
        if cat_data and "query" in cat_data and "pages" in cat_data["query"]:
            for p in cat_data["query"]["pages"].values():
                if "missing" not in p:
                    found_cats.append(p["title"])

        primary_map_cat = None
        old_map_cat = None
        for fc in found_cats:
            if "old maps" in fc.lower():
                old_map_cat = fc
            elif not primary_map_cat:
                primary_map_cat = fc

        if not primary_map_cat:
            primary_map_cat = f"Category:Maps of {name_en}"

        commons_cat_url = f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(primary_map_cat)}"
        commons_old_cat_url = f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(old_map_cat)}" if old_map_cat else None

        # 3. Search for specific scanned maps / historical maps on Commons
        # Search patterns: e.g. "<City> map" or "<City> topographic"
        search_q = f'"{name_en}" map'
        s_url = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(search_q)}&srnamespace=6&srlimit=10&format=json"
        s_data = get_json(s_url)

        scanned_maps = []
        if s_data and "query" in s_data and "search" in s_data["query"]:
            for item in s_data["query"]["search"]:
                title = item["title"]
                # Must be an image file and contain map-like terms
                t_lower = title.lower()
                if any(ext in t_lower for ext in [".jpg", ".jpeg", ".png", ".tif", ".svg"]):
                    if "map" in t_lower or "ams" in t_lower or "txu" in t_lower or "plan" in t_lower:
                        clean_name = title.replace("File:", "").replace(".jpg", "").replace(".png", "").replace(".jpeg", "")
                        scanned_maps.append({
                            "title": clean_name,
                            "file_title": title,
                            "url": f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(title)}"
                        })
                if len(scanned_maps) >= 3:
                    break

        # Fallback search if less than 1 map found
        if not scanned_maps:
            s_url2 = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(name_en + ' topographic')}&srnamespace=6&srlimit=5&format=json"
            s_data2 = get_json(s_url2)
            if s_data2 and "query" in s_data2 and "search" in s_data2["query"]:
                for item in s_data2["query"]["search"]:
                    title = item["title"]
                    if any(ext in title.lower() for ext in [".jpg", ".png", ".svg"]):
                        clean_name = title.replace("File:", "").replace(".jpg", "").replace(".png", "")
                        scanned_maps.append({
                            "title": clean_name,
                            "file_title": title,
                            "url": f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(title)}"
                        })
                    if len(scanned_maps) >= 2:
                        break

        commons_search_url = f"https://commons.wikimedia.org/w/index.php?search={urllib.parse.quote(name_en)}+map&title=Special:MediaSearch&type=image"

        results[cid] = {
            "id": cid,
            "name_en": name_en,
            "name_zh": name_zh,
            "province_en": c["province_en"],
            "wikipedia_en_title": en_page_title,
            "wikipedia_en_url": en_url,
            "wikipedia_zh_title": zh_page_title,
            "wikipedia_zh_url": zh_url,
            "wikidata_id": qid,
            "wikidata_url": wikidata_url,
            "commons_map_category": primary_map_cat,
            "commons_map_category_url": commons_cat_url,
            "commons_old_map_category": old_map_cat,
            "commons_old_map_category_url": commons_old_cat_url,
            "commons_search_maps_url": commons_search_url,
            "scanned_maps": scanned_maps
        }

        time.sleep(0.08)

    os.makedirs("data/processed", exist_ok=True)
    with open("data/processed/city_wiki_resources.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Successfully compiled Wiki & Map resources for all {len(results)} cities into data/processed/city_wiki_resources.json!")

if __name__ == "__main__":
    main()
