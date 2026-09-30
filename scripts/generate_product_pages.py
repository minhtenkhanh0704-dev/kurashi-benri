import json
import re
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS_FILE = ROOT / "products.json"
PRODUCTS_DIR = ROOT / "products"
CATEGORIES_DIR = ROOT / "categories"
SITEMAP_FILE = ROOT / "sitemap.xml"
BASE_URL = "https://minhtenkhanh0704-dev.github.io/kurashi-benri"
TODAY = date.today().isoformat()


def slug_for(product):
    raw = str(product.get("id") or "")
    slug = re.sub(r"[^A-Za-z0-9_-]+", "-", raw).strip("-_").lower()
    return slug or "product"


def price_number(value):
    m = re.search(r"[0-9][0-9,]*", str(value or ""))
    return m.group(0).replace(",", "") if m else None

CATEGORY_SLUGS = {
    "収納": "storage",
    "キッチン": "kitchen",
    "掃除": "cleaning",
    "一人暮らし": "solo-living",
    "PC・デスク": "pc-desk",
    "旅行": "travel",
}

CATEGORY_DESCRIPTIONS = {
    "収納": "部屋やクローゼットをすっきり整理するための収納ボックス・収納ケースなどの便利グッズを紹介します。",
    "キッチン": "料理や片付けを快適にするキッチン収納・調理便利グッズを紹介します。",
    "掃除": "毎日の掃除や排水口のお手入れなどをラクにする便利グッズを紹介します。",
    "一人暮らし": "一人暮らしの部屋づくり・収納・キッチンなどに役立つ便利グッズを紹介します。",
    "PC・デスク": "PC作業や勉強環境を快適にするデスク周りの便利グッズを紹介します。",
    "旅行": "旅行や出張の荷物整理をラクにするトラベル便利グッズを紹介します。",
}

def category_slug(category):
    return CATEGORY_SLUGS.get(category, "category")

def category_html(category, products):
    slug = category_slug(category)
    items = [
        p for p in products
        if str(p.get("cat") or "").strip() == category
    ]

    description = CATEGORY_DESCRIPTIONS.get(
        category,
        f"{category}の便利グッズ・おすすめ商品を紹介します。"
    )

    canonical = f"{BASE_URL}/categories/{slug}.html"

    cards = []

    for p in items:
        pslug = slug_for(p)
        title = str(p.get("title") or "おすすめ商品").strip()
        desc = str(p.get("desc") or "楽天市場で人気の便利アイテム。").strip()
        price = str(p.get("price") or "価格は商品ページで確認").strip()
        image = str(p.get("image") or "").strip()

        image_html = (
            f'<img src="{escape(image, quote=True)}" '
            f'alt="{escape(title, quote=True)}" '
            'width="320" height="240" loading="lazy" decoding="async">'
            if image else ""
        )

        cards.append(
            f'<a class="category-card" href="{BASE_URL}/products/{pslug}.html">'
            f'<div class="category-image">{image_html}</div>'
            f'<div class="category-tag">{escape(category)}</div>'
            f'<h2>{escape(title)}</h2>'
            f'<p>{escape(desc)}</p>'
            f'<div class="category-price">{escape(price)}</div>'
            '</a>'
        )

    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(category)}の便利グッズ・おすすめ商品｜暮らし便利帳</title>
<meta name="description" content="{escape(description, quote=True)}">
<link rel="canonical" href="{escape(canonical, quote=True)}">
<meta property="og:type" content="website">
<meta property="og:title" content="{escape(category)}の便利グッズ・おすすめ商品｜暮らし便利帳">
<meta property="og:description" content="{escape(description, quote=True)}">
<meta property="og:url" content="{escape(canonical, quote=True)}">
<meta property="og:site_name" content="暮らし便利帳">

<style>
:root{{--bg:#f7f7f8;--card:#fff;--text:#18181b;--muted:#71717a;--line:#e4e4e7;--accent:#e60012}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,BlinkMacSystemFont,"Noto Sans JP",sans-serif}}
.wrap{{max-width:1100px;margin:auto;padding:0 20px}}
header{{background:#fff;border-bottom:1px solid var(--line);padding:18px 0}}
.brand{{font-weight:900;font-size:21px;text-decoration:none;color:var(--text)}}
.brand span{{color:var(--accent)}}
main{{padding:34px 0 70px}}
.crumb{{font-size:13px;color:var(--muted);margin-bottom:16px}}
.crumb a{{color:inherit}}
h1{{font-size:clamp(28px,5vw,44px);margin:0 0 12px}}
.lead{{color:#52525b;line-height:1.8;margin-bottom:28px}}
.category-grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}}
.category-card{{display:block;background:#fff;border:1px solid var(--line);border-radius:16px;overflow:hidden;text-decoration:none;color:inherit}}
.category-image{{aspect-ratio:4/3;background:#fff;display:grid;place-items:center;padding:10px}}
.category-image img{{width:100%;height:100%;object-fit:contain}}
.category-tag{{color:var(--accent);font-size:11px;font-weight:800;padding:12px 14px 0}}
.category-card h2{{font-size:16px;line-height:1.5;margin:6px 14px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}}
.category-card p{{font-size:13px;color:#52525b;line-height:1.5;margin:0 14px 10px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.category-price{{font-size:17px;font-weight:900;padding:0 14px 16px}}
footer{{padding:26px 0;border-top:1px solid var(--line);color:var(--muted);font-size:12px;background:#fff}}
@media(max-width:900px){{.category-grid{{grid-template-columns:repeat(3,minmax(0,1fr))}}}}
@media(max-width:700px){{.wrap{{padding:0 14px}}.category-grid{{grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}}}}
@media(max-width:480px){{.category-grid{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<header>
<div class="wrap">
<a class="brand" href="{BASE_URL}/">暮らし<span>便利帳</span></a>
</div>
</header>

<main>
<div class="wrap">
<div class="crumb"><a href="{BASE_URL}/">ホーム</a> / {escape(category)}</div>
<h1>{escape(category)}の便利グッズ・おすすめ商品</h1>
<p class="lead">{escape(description)}</p>

<div class="category-grid">
{"".join(cards)}
</div>

</div>
</main>

<footer>
<div class="wrap">© 2026 暮らし便利帳</div>
</footer>
</body>
</html>
"""
def page_html(product, slug, all_products):
    title = str(product.get("title") or "おすすめ商品").strip()
    category = str(product.get("cat") or "便利グッズ").strip()
    desc = str(product.get("desc") or "楽天市場で人気の便利アイテム。").strip()
    price = str(product.get("price") or "価格は商品ページで確認").strip()
    image = str(product.get("image") or "").strip()
    url = str(product.get("url") or "#").strip()
    canonical = f"{BASE_URL}/products/{slug}.html"
    price_value = price_number(price)

    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": title,
        "description": f"{title}。{category}カテゴリの便利グッズ。価格・在庫・仕様は楽天市場の商品ページでご確認ください。",
        "sku": str(product.get("id") or slug),
    }
    if image:
        schema["image"] = [image]
    brand = str(product.get("brand") or "").strip()
    gtin = str(product.get("gtin") or "").strip()
    availability = product.get("availability")

    schema["category"] = category
    schema["url"] = canonical

    if brand:
        schema["brand"] = {
            "@type": "Brand",
            "name": brand,
        }

    if gtin:
        schema["gtin"] = gtin

    if price_value and url != "#":
        offer = {
            "@type": "Offer",
            "url": url,
            "priceCurrency": "JPY",
            "price": price_value,
        }

        if availability in (1, "1", True):
            offer["availability"] = "https://schema.org/InStock"
        elif availability in (0, "0", False):
            offer["availability"] = "https://schema.org/OutOfStock"

        schema["offers"] = offer

    schema_json = json.dumps(
        schema,
        ensure_ascii=False,
        separators=(",", ":")
    )

    image_html = (
        f'<img src="{escape(image, quote=True)}" alt="{escape(title, quote=True)}" '
        'width="640" height="480" loading="eager" decoding="async">'
        if image else ""
    )

    buy_html = (
        f'<a class="buy" href="{escape(url, quote=True)}" target="_blank" '
        'rel="nofollow sponsored noopener">楽天市場で商品を見る</a>'
        if url != "#" else
        '<span class="buy disabled">商品ページ準備中</span>'
    )

    related = [
        p for p in all_products
        if slug_for(p) != slug
        and str(p.get("cat") or "便利グッズ").strip() == category
    ][:4]

    if len(related) < 4:
        for p in all_products:
            if slug_for(p) == slug or p in related:
                continue
            related.append(p)
            if len(related) >= 4:
                break

    related_cards = ""

    if related:
        cards = []

        for p in related:
            rslug = slug_for(p)
            rtitle = str(p.get("title") or "おすすめ商品").strip()
            rcat = str(p.get("cat") or "便利グッズ").strip()
            rimage = str(p.get("image") or "").strip()

            rimage_html = (
                f'<img src="{escape(rimage, quote=True)}" '
                f'alt="{escape(rtitle, quote=True)}" '
                'width="220" height="165" loading="lazy" decoding="async">'
                if rimage else ""
            )

            cards.append(
                f'<a class="related-card" href="{BASE_URL}/products/{rslug}.html">'
                f'<div class="related-image">{rimage_html}</div>'
                f'<div class="related-cat">{escape(rcat)}</div>'
                f'<div class="related-title">{escape(rtitle)}</div>'
                f'<div class="related-price">{escape(str(p.get("price") or "価格は商品ページで確認"))}</div>'
                '</a>'
            )

        related_cards = (
            '<section class="related">'
            '<h2>こちらの商品もおすすめ</h2>'
            '<div class="related-grid">'
            + "".join(cards)
            + '</div></section>'
        )
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}｜暮らし便利帳</title>
<meta name="description" content="{escape(title + '。' + category + 'の便利グッズ。価格・在庫・仕様は楽天市場の商品ページで確認できます。', quote=True)}">
<link rel="canonical" href="{escape(canonical, quote=True)}">
<meta property="og:type" content="product">
<meta property="og:title" content="{escape(title + '｜暮らし便利帳', quote=True)}">
<meta property="og:description" content="{escape(category + 'の便利グッズ。価格・在庫・仕様は楽天市場の商品ページで確認できます。', quote=True)}">
<meta property="og:url" content="{escape(canonical, quote=True)}">
<meta property="og:site_name" content="暮らし便利帳">
<meta property="og:locale" content="ja_JP">
{f'<meta property="og:image" content="{escape(image, quote=True)}">' if image else ''}
<script type="application/ld+json">{schema_json}</script>
<style>
:root{{--bg:#f7f7f8;--card:#fff;--text:#18181b;--muted:#71717a;--line:#e4e4e7;--accent:#e60012}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,BlinkMacSystemFont,"Noto Sans JP",sans-serif}}
.wrap{{max-width:900px;margin:auto;padding:0 20px}}header{{background:#fff;border-bottom:1px solid var(--line);padding:18px 0}}
.brand{{font-weight:900;font-size:21px;text-decoration:none}}.brand span{{color:var(--accent)}}
main{{padding:30px 0 70px}}.crumb{{font-size:13px;color:var(--muted);margin-bottom:18px}}.crumb a{{color:inherit}}
.card{{background:#fff;border:1px solid var(--line);border-radius:20px;overflow:hidden}}
.photo{{background:#fff;padding:20px;text-align:center}}.photo img{{max-width:100%;height:auto;max-height:520px;object-fit:contain}}
.body{{padding:24px}}.tag{{display:inline-block;color:var(--accent);font-weight:800;font-size:13px;margin-bottom:8px}}
h1{{font-size:clamp(26px,5vw,42px);line-height:1.35;margin:0 0 16px}}.desc{{color:#52525b;line-height:1.8}}
.price{{font-size:24px;font-weight:900;margin:20px 0}}.highlights{{margin:24px 0;padding:18px;background:#fff7f7;border:1px solid #ffd6d6;border-radius:14px}}
.highlights h2{{font-size:18px;margin:0 0 10px}}
.highlights ul{{margin:0;padding-left:20px;color:#52525b;line-height:1.8}}.note{{color:var(--muted);font-size:13px;line-height:1.7}}
.buy{{display:inline-block;margin-top:12px;padding:13px 18px;background:var(--accent);color:#fff;text-decoration:none;border-radius:10px;font-weight:800}}
.buy.disabled{{background:#ddd;color:#555}}

.related{{margin-top:30px}}
.related h2{{font-size:22px;margin:0 0 14px}}

.related-grid{{
  display:grid;
  grid-template-columns:repeat(4,minmax(0,1fr));
  gap:12px;
}}

.related-card{{
  display:block;
  background:#fff;
  border:1px solid var(--line);
  border-radius:14px;
  overflow:hidden;
  text-decoration:none;
  color:inherit;
}}

.related-image{{
  aspect-ratio:4/3;
  display:grid;
  place-items:center;
  background:#fff;
  padding:8px;
}}

.related-image img{{
  width:100%;
  height:100%;
  object-fit:contain;
}}

.related-cat{{
  padding:10px 12px 0;
  color:var(--accent);
  font-size:11px;
  font-weight:800;
}}

.related-title{{
  padding:5px 12px 12px;
  font-size:14px;
  font-weight:800;
  line-height:1.45;
}}
.related-price{{
  padding:0 12px 14px;
  font-size:16px;
  font-weight:900;
}}
@media(max-width:700px){{
  .related-grid{{
    grid-template-columns:repeat(2,minmax(0,1fr));
  }}
}}

footer{{padding:25px 0;border-top:1px solid var(--line);color:var(--muted);font-size:12px;background:#fff}}
@media(max-width:540px){{.wrap{{padding:0 14px}}.body{{padding:18px}}}}
</style>
</head>
<body>
<header><div class="wrap"><a class="brand" href="{BASE_URL}/">暮らし<span>便利帳</span></a></div></header>
<main><div class="wrap">
<div class="crumb"><a href="{BASE_URL}/">ホーム</a> / {escape(category)}</div>
<article class="card">
<div class="photo">{image_html}</div>
<div class="body">
<div class="tag">{escape(category)}</div>
<h1>{escape(title)}</h1>
<p class="desc">{escape(desc)}</p>

<div class="highlights">
  <h2>おすすめポイント</h2>
  <ul>
    <li>{escape(desc)}</li>
    <li>{escape(category)}で使いやすい便利アイテム</li>
    <li>一人暮らしや毎日の生活にも取り入れやすい商品</li>
  </ul>
</div>

<div class="price">{escape(price)}</div>
<p class="note">商品情報・価格・在庫・仕様は変わる場合があります。購入前に楽天市場の商品ページで最新情報をご確認ください。</p>
{buy_html}
<p class="note">PR：当ページにはアフィリエイトリンクが含まれます。</p>
</div>
</article>
{related_cards}
</div></main>
<footer><div class="wrap">© 2026 暮らし便利帳</div></footer>
</body>
</html>
"""


def main():
    data = json.loads(PRODUCTS_FILE.read_text(encoding="utf-8"))
    products = data.get("products", [])

    PRODUCTS_DIR.mkdir(exist_ok=True)
    CATEGORIES_DIR.mkdir(exist_ok=True)

    for old in CATEGORIES_DIR.glob("*.html"):
        old.unlink()

    for old in PRODUCTS_DIR.glob("*.html"):
        old.unlink()

    urls = [f"{BASE_URL}/"]

    categories = []

    for product in products:
        category = str(product.get("cat") or "").strip()

        if category and category not in categories:
            categories.append(category)

    for category in categories:
        slug = category_slug(category)

        (CATEGORIES_DIR / f"{slug}.html").write_text(
            category_html(category, products),
            encoding="utf-8"
        )

        urls.append(
            f"{BASE_URL}/categories/{slug}.html"
        )

    for product in products:
        slug = slug_for(product)

        (PRODUCTS_DIR / f"{slug}.html").write_text(
            page_html(product, slug, products),
            encoding="utf-8"
        )

        urls.append(
            f"{BASE_URL}/products/{slug}.html"
        )

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        f"  <url><loc>{BASE_URL}/</loc><lastmod>{TODAY}</lastmod><changefreq>daily</changefreq><priority>1.0</priority></url>",
    ]

    for url in urls[1:]:
        lines.append(
            f"  <url><loc>{escape(url)}</loc><lastmod>{TODAY}</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>"
        )

    lines.append("</urlset>")

    SITEMAP_FILE.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8"
    )

    print(
        f"Generated {len(products)} product pages and sitemap with {len(urls)} URLs."
    )

if __name__ == "__main__":
    main()
