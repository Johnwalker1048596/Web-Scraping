from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json   

def search_pchome(keyword: str, max_items: int = 10):
    """
    Use Selenium to search PChome.
    Returns:
      - If found: list[dict], each {name, price, img, link}
      - If nothing: "無此商品"
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--incognito")
    options.add_argument("--disable-popup-blocking")

    driver = webdriver.Chrome(options=options)
    CARD = ".c-prodInfoV2.c-prodInfoV2--gridCard"

    try:
        # Go to search result page
        driver.get(f"https://24h.pchome.com.tw/search/?q={keyword}")
        time.sleep(3)

        # First batch of product cards
        items = driver.find_elements(By.CSS_SELECTOR, CARD)
        if not items:
            return "無此商品"

        last = items[-1]

        # Scroll down until no new items or enough items
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            new_items = driver.find_elements(By.CSS_SELECTOR, CARD)
            if not new_items or new_items[-1] == last or len(new_items) >= max_items * 3:
                items = new_items
                break

            items = new_items
            last = items[-1]

        results = []

        for card in items:
            # Scroll this card into view to trigger lazy-load image
            driver.execute_script("arguments[0].scrollIntoView();", card)
            time.sleep(0.2)

            # Name
            name = card.find_element(By.CSS_SELECTOR, ".c-prodInfoV2__title").text
            if keyword not in name:
                continue

            # Price
            price = card.find_element(
                By.CSS_SELECTOR,
                ".c-prodInfoV2__priceValue.c-prodInfoV2__priceValue--m"
            ).text

            # Image (handle mobile_loading.svg lazy-load)
            img_el = card.find_element(By.CSS_SELECTOR, ".c-prodInfoV2__img img")
            img = img_el.get_attribute("src") or ""
            if "mobile_loading.svg" in img:
                for attr in ("data-src", "data-srcset", "srcset"):
                    v = img_el.get_attribute(attr)
                    if v:
                        img = v.split(",")[0].strip().split(" ")[0]
                        break
            if not img:
                img = "無圖片"

            # Product link
            link = card.find_element(
                By.CSS_SELECTOR,
                "a.c-prodInfoV2__link.gtmClickV2"
            ).get_attribute("href")

            results.append({
                "name": name,
                "price": price,
                "img": img,
                "link": link
            })

            if len(results) >= max_items:
                break

        # ---- ★ Save to JSON here ★ ----
        if results:
            filename = f"{keyword}.json"   # e.g. "衛生紙.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
            return results
        else:
            return "無此商品"

    finally:
        driver.quit()


if __name__ == "__main__":
    kw = "洋芋片"
    data = search_pchome(kw, max_items=50)

    if isinstance(data, str):
        # e.g. "無此商品"
        print(f"關鍵字「{kw}」搜尋結果：{data}")
    else:
        print(f"關鍵字「{kw}」找到 {len(data)} 筆商品：\n")
        for i, item in enumerate(data, start=1):
            print(f"第 {i} 筆")
            print(f"  名稱：{item['name']}")
            print(f"  價格：{item['price']}")
            print(f"  連結：{item['link']}")
            print(f"  圖片：{item['img']}")
            print("-" * 50)
