import requests
import urllib.parse
import json

def search_item(keyword):
    # 關鍵字做 URL 編碼
    kw = urllib.parse.quote(keyword)

    api_url = f"https://ecshweb.pchome.com.tw/search/v3.3/all/results?q={kw}&page=1&sort=rnk/dc"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    r = requests.get(api_url, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()

    prods = data.get("prods") or []
    if not prods:
        return "無此商品"

    results = []

    for item in prods[:25]:
        name = item.get("name", "無資料")
        price = item.get("price", "無資料")

        product_id = item.get("Id", "")
        url = f"https://24h.pchome.com.tw/prod/{product_id}" if product_id else ""

        # 圖片路徑：用 picB / picS，前綴改成 cs-a.ecimg.tw
        pic_path = item.get("picB") or item.get("picS") or ""
        img = f"https://cs-a.ecimg.tw{pic_path}" if pic_path else ""

        results.append({
            "name": name,
            "price": price,
            "url": url,
            "img": img
        })

    # 存成 JSON 檔
    filename = f"{keyword}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    return results


# 測試
data = search_item("牛奶")
if isinstance(data, str):
    print(data)
else:
    for i, item in enumerate(data, 1):
        print(f"第 {i} 筆：")
        print(f"  名稱：{item['name']}")
        print(f"  價格：{item['price']}")
        print(f"  商品：{item['url']}")
        print(f"  圖片：{item['img']}")
        print("-" * 40)
