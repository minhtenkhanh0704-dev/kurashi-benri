import json
import re
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS_FILE = ROOT / "products.json"
PRODUCTS_DIR = ROOT / "products"
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
    if price_value and url != "#":
        schema["offers"] = {
            "@type": "Offer",
            "url": url,
            "priceCurrency": "JPY",
            "price": price_value,
        }

    schema_json = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))

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
                '</a>'
            )

        related_cards = (
            '<section class="related">'
            '<h2>こちらの商品もおすすめ</h2>'
            '<div class="related-grid">'
            + "".join(cards) +
            '</div></section>'
        )
    return f"""<!doctype html>
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
.price{{font-size:24px;font-weight:900;margin:20px 0}}.note{{color:var(--muted);font-size:13px;line-height:1.7}}
.buy{{display:inline-block;margin-top:12px;padding:13px 18px;background:var(--accent);color:#fff;text-decoration:none;border-radius:10px;font-weight:800}}
.buy.disabled{{background:#ddd;color:#555}}footer{{padding:25px 0;border-top:1px solid var(--line);color:var(--muted);font-size:12px;background:#fff}}
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

    for old in PRODUCTS_DIR.glob("*.html"):
        old.unlink()

    urls = [f"{BASE_URL}/"]
    for product in products:
        slug = slug_for(product)
        (PRODUCTS_DIR / f"{slug}.html").write_text(
            page_html(product, slug, products), encoding="utf-8"
        )
        urls.append(f"{BASE_URL}/products/{slug}.html")

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
    SITEMAP_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Generated {len(products)} product pages and sitemap with {len(urls)} URLs.")


if __name__ == "__main__":
    main()
