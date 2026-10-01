import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError
API_URL = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260701"
OUT = Path("products.json")

APPLICATION_ID = os.environ["RAKUTEN_APPLICATION_ID"]
ACCESS_KEY = os.environ["RAKUTEN_ACCESS_KEY"]
AFFILIATE_ID = os.environ["RAKUTEN_AFFILIATE_ID"]

SEARCHES = [
    ("収納ボックス 収納ケース 整理", "収納"),
("キッチン 便利グッズ 調理 収納", "キッチン"),
("掃除 便利グッズ 排水 掃除", "掃除"),
("一人暮らし 便利グッズ 省スペース", "一人暮らし"),
("PC デスク 便利グッズ", "PC・デスク"),
("旅行 トラベル 便利グッズ", "旅行"),
]

def api_search(keyword):
    params = {
        "format": "json",
        "keyword": keyword,
        "applicationId": APPLICATION_ID,
        "accessKey": ACCESS_KEY,
        "formatVersion": 2,
        "hits": 30,
        "sort": "-updateTimestamp",
        "availability": 1,
        "affiliateId": AFFILIATE_ID,
    }

    url = API_URL + "?" + urlencode(params)

    req = Request(
        url,
        headers={
            "User-Agent": "kurashi-benri/1.0",
            "Accept": "application/json",
        },
    )

    try:
        with urlopen(req, timeout=30) as response:
            return json.load(response)

    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Rakuten API HTTP {e.code}: {body}"
        ) from e


def clean_title(title):
    title = " ".join((title or "").split())
    return title[:95] + ("…" if len(title) > 95 else "")


def make_desc(item):
    rating = item.get("reviewAverage")
    reviews = item.get("reviewCount", 0)

    if rating and reviews:
        return f"★{rating}｜{reviews:,}件のレビュー"
    elif rating:
        return f"★{rating}"
    elif reviews:
        return f"{reviews:,}件のレビュー"
    else:
        return "楽天市場で人気の便利アイテム。"

def main():
    found = {}

    for keyword, category in SEARCHES:
        try:
            data = api_search(keyword)

            items = data.get("Items", data.get("items", []))

            for item in items:

                if "item" in item and isinstance(item["item"], dict):
                    item = item["item"]

                code = item.get("itemCode") or item.get("itemUrl")

                if not code:
                    continue

                affiliate_url = (
                    item.get("affiliateUrl")
                    or item.get("itemUrl")
                )

                image_urls = (
                    item.get("mediumImageUrls")
                    or item.get("smallImageUrls")
                    or []
                )

                image = image_urls[0].split("?_ex=")[0] if image_urls else ""

                price = item.get("itemPrice")

                if not affiliate_url:
                    continue

                if not item.get("itemName"):
                    continue

            

                candidate = {
                    "id": code,
                    "cat": category,
                    "title": clean_title(item["itemName"]),
                    "desc": make_desc(item),
                    "price": (
                        f"{int(price):,}円"
                        if isinstance(price, (int, float))
                        else "価格は商品ページで確認"
                    ),
                    "url": affiliate_url,
                    "image": image,
                    "availability": item.get("availability"),
                    "updateTimestamp": item.get("updateTimestamp"),
                    "brand": item.get("brand"),
                    "gtin": item.get("gtin") or item.get("janCode"),
                }

                candidate = {
                    k: v for k, v in candidate.items()
                    if v not in (None, "")
                }

                if code not in found:
                    found[code] = candidate

        except Exception as e:
            print(
                f"[WARN] search failed: {keyword}: {e}",
                file=sys.stderr
            )

        time.sleep(2.0)

    products = list(found.values())

    unique_products = []
    seen_images = set()
    seen_titles = set()

    def normalize_text(value):
        return " ".join(str(value or "").lower().split())

    def image_fingerprint(value):
        value = str(value or "").strip().lower()

        if not value:
            return ""

        marker = "/@0_mall/"

        if marker in value:
            value = value.split(marker, 1)[1]
            parts = value.split("/", 1)

            if len(parts) == 2:
                value = parts[1]

        return value.split("?", 1)[0]

    for product in products:
        image = image_fingerprint(product.get("image"))
        title = normalize_text(product.get("title"))

        if image and image in seen_images:
            continue

        if title and title in seen_titles:
            continue

        if image:
            seen_images.add(image)

        if title:
            seen_titles.add(title)

        unique_products.append(product)

    products = unique_products

    by_cat = {}

    for product in products:
        by_cat.setdefault(product["cat"], []).append(product)

    selected = []
    selected_images = set()
    selected_titles = set()

    def add_unique(product):
        image = image_fingerprint(product.get("image"))
        title = normalize_text(product.get("title"))

        if image and image in selected_images:
            return False

        if title and title in selected_titles:
            return False

        selected.append(product)

        if image:
            selected_images.add(image)

        if title:
            selected_titles.add(title)

        return True

    for _, category in SEARCHES:
        category_count = 0

        for product in by_cat.get(category, []):
            if category_count >= 8:
                break

            if add_unique(product):
                category_count += 1

    for product in products:
        if len(selected) >= 48:
            break

        add_unique(product)
    if not selected:
        raise RuntimeError(
            "Rakuten API returned no products. "
            "Refusing to overwrite products.json."
        )
    payload = {
        "products": selected[:48]
    }

    OUT.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2
        ) + "\n",
        encoding="utf-8"
    )

    print(
        f"Wrote {len(selected[:48])} products to {OUT}"
    )


if __name__ == "__main__":
    main()
