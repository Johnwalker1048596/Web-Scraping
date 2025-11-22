from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, json

#  第一階段：抓 PChome 搜尋頁所有商品資料（含可能為 null 的圖片）

def crawl_search_list(keyword):

    print("\n=====【階段 1：抓搜尋頁所有商品】=====\n")

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

    results = []

    for page in range(1, 200):
        print(f"=== 抓第 {page} 頁 ===")

        url = f"https://24h.pchome.com.tw/search/?q={keyword}&p={page}"
        driver.get(url)

        # 等待商品載入
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    ".c-prodInfoV2__title, .c-product__name"
                ))
            )
        except:
            print("頁面無商品 → 停止")
            break

        time.sleep(1)

        # 抓兩種 layout
        cards1 = driver.find_elements(By.CSS_SELECTOR, ".c-prodInfoV2")
        cards2 = driver.find_elements(By.CSS_SELECTOR, ".c-product")
        cards = cards1 + cards2

        print("本頁商品數：", len(cards))
        is_last_page = len(cards) < 40  

        # 將每個卡片的基本資料抓起來
        for card in cards:

            # 強制滾動確保資料顯示
            driver.execute_script("arguments[0].scrollIntoView();", card)
            time.sleep(0.15)

            # 名稱
            try:
                name = card.find_element(
                    By.CSS_SELECTOR,
                    ".c-prodInfoV2__title, .c-product__name"
                ).text.strip()
            except:
                name = ""

            # 價格
            try:
                price = card.find_element(
                    By.CSS_SELECTOR,
                    ".c-prodInfoV2__priceValue--m, .c-product__price"
                ).text.strip()
            except:
                price = ""

            # 連結
            try:
                link = card.find_element(
                    By.CSS_SELECTOR,
                    "a.c-prodInfoV2__link, a.c-product__img, a"
                ).get_attribute("href")
            except:
                link = ""

            # 圖片（列表頁先抓，有可能為 null）
            img = None
            try:
                container = card.find_element(
                    By.CSS_SELECTOR,
                    ".c-prodInfoV2__img, .c-product__img"
                )

                # <img> 標籤
                try:
                    img_tag = container.find_element(By.TAG_NAME, "img")
                    img = img_tag.get_attribute("src")
                    if img and "loading.svg" in img:
                        img = img_tag.get_attribute("data-src")
                except:
                    pass

                # 背景圖片
                if not img:
                    style = container.get_attribute("style")
                    if "background-image" in style:
                        img = style.split("url(")[1].split(")")[0].strip('"').strip("'")

            except:
                img = None

            results.append({
                "name": name,
                "price": price,
                "link": link,
                "img": img
            })

        if is_last_page:
            print("→ 已到最後一頁，停止")
            break

        time.sleep(1)

    driver.quit()
    print(f"\n✔ 階段 1 完成，共 {len(results)} 筆商品\n")
    return results

#  第二階段：補上所有 null 圖片（進入商品頁抓封面）

def fill_cover_images(results):

    print("\n=====【階段 2：補圖片（抓商品頁封面）】=====\n")

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

    for item in results:

        if item["img"]:   # 若列表頁已有圖片 → 跳過
            continue

        link = item["link"]
        if not link:
            continue

        print(f"→ 列表無圖片，進入商品頁補抓：{link}")

        try:
            driver.get(link)

            WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".pic-main img"))
            )
            time.sleep(0.4)

            cover = driver.find_element(By.CSS_SELECTOR, ".pic-main img").get_attribute("src")
            item["img"] = cover

        except:
            print("   ❌ 補抓失敗")
            item["img"] = None

    driver.quit()
    print("\n✔ 階段 2 完成（圖片補抓結束）\n")
    return results

def search_pchome_final(keyword):

    data = crawl_search_list(keyword)
    data = fill_cover_images(data)

    filename = f"{keyword}_final.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n🎉【全部完成！】")
    print(f"✔ 最終筆數：{len(data)}")
    print(f"✔ 已輸出：{filename}")

    return data

search_pchome_final("衛生紙")
