#!/usr/bin/env python3
"""Zet de Kirby-content van Studio 4 Holland om naar Astro content collections.

Gebruik (vanuit de map st4hl-astro):

    python3 scripts/kirby2astro.py ../st4hl/content

- Elke Kirby-pagina wordt een map met index.md (Nederlands, volledig) en,
  als er een Engelse versie is, index.en.md (alleen wat anders is).
- Afbeeldingen komen naast de Markdown te staan; Astro maakt er bij het bouwen
  AVIF- en WebP-versies van.
- Het script is opnieuw te draaien: het overschrijft src/content/sections en
  src/content/items volledig. Handmatige wijzigingen daar gaan dan verloren,
  dus draai het alleen voor een (nieuwe) import vanuit Kirby.

Vereist: Python 3, PyYAML en markdownify (pip install pyyaml markdownify).
"""
import html
import json
import re
import shutil
import sys
from pathlib import Path

import yaml
from markdownify import markdownify

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src" / "content"
SRC = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else (ROOT.parent / "st4hl" / "content")

IMG_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
LANGS = ("nl", "en")
# Kirby-templates per soort pagina
SECTION_TEMPLATES = {"speakers", "turntables", "hextech-feet", "repairs", "connections", "interiors"}
ITEM_TEMPLATES = {"speaker", "turntable", "hextech-foot", "repair", "connection", "interior"}
SKIP_DIRS = {"login", "error"}

UITGELICHT: set = set()
TE_KOOP: set = set()
stats = {"secties": 0, "items": 0, "afbeeldingen": 0, "zonder_engels": [], "lege_tekst": []}


# ── Kirby lezen ─────────────────────────────────────────────

def parse_kirby(path: Path) -> dict:
    """Kirby .txt → {veldnaam (kleine letters): waarde}"""
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
    fields = {}
    for chunk in re.split(r"\n----\s*\n", "\n" + text):
        chunk = chunk.strip("\n")
        m = re.match(r"^\s*([A-Za-z][\w-]*):[ \t]*(.*)$", chunk, re.S)
        if m:
            fields[m.group(1).lower()] = m.group(2).strip()
    return fields


def kirby_list(value: str) -> list:
    """'- a.jpg' / YAML-lijst / 'a, b' → ['a.jpg']"""
    if not value:
        return []
    try:
        data = yaml.safe_load(value)
    except Exception:
        data = None
    if isinstance(data, list):
        return [str(x).strip() for x in data if str(x).strip()]
    return [v.strip() for v in value.split(",") if v.strip()]


def kirbytext(s: str) -> str:
    s = re.sub(r"\(link:\s*(\S+)(?:\s+text:\s*([^)]*))?\)", lambda m: f"[{(m.group(2) or m.group(1)).strip()}]({m.group(1)})", s)
    s = re.sub(r"\(email:\s*(\S+)(?:\s+text:\s*([^)]*))?\)", lambda m: f"[{(m.group(2) or m.group(1)).strip()}](mailto:{m.group(1)})", s)
    s = re.sub(r"\(date:\s*Year\)", "{year}", s)
    return s


def html_to_md(s: str) -> str:
    if "<" not in s:
        return kirbytext(s).strip()
    md = markdownify(s, heading_style="ATX", bullets="-", strip=["span", "div"])
    md = re.sub(r"\n{3,}", "\n\n", md)
    md = re.sub(r"[ \t]+\n", "\n", md)          # spaties aan het eind (geen harde regelovergang)
    return html.unescape(md).strip()


def clean_markdown(s: str) -> str:
    # "#####* tekst" was in Kirby bedoeld als opsomming
    s = re.sub(r"^#{1,6}\*\s*", "- ", s, flags=re.M)
    return kirbytext(s).strip()


def strip_tags(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


# ── Blokken → Markdown ──────────────────────────────────────

def blocks_to_md(raw: str):
    """Geeft (markdown, galerij-volgorde, inline-afbeeldingen) terug, of None als er geen blokken zijn."""
    raw = (raw or "").strip()
    if not raw.startswith("["):
        return None
    try:
        blocks = json.loads(raw)
    except Exception:
        return None
    parts, gallery, inline = [], [], []
    for b in blocks:
        if b.get("isHidden"):
            continue
        t, c = b.get("type"), b.get("content") or {}
        if t == "heading":
            lvl = max(2, int(str(c.get("level", "h2")).lstrip("h") or 2))
            txt = strip_tags(c.get("text", ""))
            if txt:
                parts.append("#" * lvl + " " + txt)
        elif t in ("text", "list"):
            md = html_to_md(c.get("text", ""))
            if md:
                parts.append(md)
        elif t == "markdown":
            md = clean_markdown(c.get("text", ""))
            if md:
                parts.append(md)
        elif t == "quote":
            q = html_to_md(c.get("text", ""))
            cite = strip_tags(c.get("citation", ""))
            if q:
                parts.append("\n".join("> " + line if line else ">" for line in q.splitlines()) + (f"\n>\n> — {cite}" if cite else ""))
        elif t == "image":
            if c.get("location") == "web" and c.get("src"):
                parts.append(f"![{c.get('alt', '')}]({c['src']})")
            for f in kirby_list(json.dumps(c.get("image") or [])) if isinstance(c.get("image"), list) else []:
                inline.append(f)
                parts.append(f"![{strip_tags(c.get('alt', '')) or strip_tags(c.get('caption', ''))}]({slug_file(f)})")
        elif t == "gallery":
            gallery += [str(x) for x in (c.get("images") or [])]
        else:
            txt = c.get("text") if isinstance(c, dict) else None
            if txt:
                parts.append(html_to_md(txt))
    return "\n\n".join(p for p in parts if p).strip(), gallery, inline


def body_of(fields: dict):
    res = blocks_to_md(fields.get("blocks", ""))
    if res and res[0]:
        return res
    gallery, inline = (res[1], res[2]) if res else ([], [])
    for key in ("text", "body"):
        v = fields.get(key, "").strip()
        if v and not v.startswith("["):
            return html_to_md(v), gallery, inline
    return "", gallery, inline


STRUCTURE = re.compile(r"^\s*([-*+>#|]|\d+[.)]\s|!\[)")


def reflow(md: str) -> str:
    """Kirby zette elke Enter om in een <br>. Veel teksten zijn halverwege een zin afgebroken
    ("thought it would be a cool / idea"); die regels plakken we aan elkaar. Een nieuwe regel
    na een korte regel of na een leesteken blijft een bewuste regelovergang."""
    out = []
    for line in md.split("\n"):
        prev = out[-1] if out else ""
        if (out and line.strip() and prev.strip() and not STRUCTURE.match(line) and not STRUCTURE.match(prev)
                and not re.search(r"[.!?:,;]\s*$", prev)
                and (re.match(r"^[a-z(“\"'‘]", line.strip()) or len(prev.strip()) >= 60)):
            out[-1] = prev.rstrip() + " " + line.strip()
        else:
            out.append(line.rstrip())
    # Bewuste regelovergangen binnen een alinea worden een harde enter (backslash aan het eind,
    # standaard Markdown), zodat het met elke Markdown-verwerker en elk CMS hetzelfde blijft.
    for n in range(len(out) - 1):
        a, b = out[n], out[n + 1]
        if a.strip() and b.strip() and not STRUCTURE.match(a) and not STRUCTURE.match(b) and not a.endswith("\\"):
            out[n] = a + "\\"
    return "\n".join(out)


def is_filler(md: str) -> bool:
    """'cccccc' en andere opvultekst uit het Kirby-paneel"""
    plain = re.sub(r"\W", "", md)
    return bool(plain) and len(set(plain.lower())) == 1


# ── Bestanden ───────────────────────────────────────────────

def slug_file(name: str) -> str:
    """Bestandsnamen zonder spaties of hoofdletters (WhatsApp Image … .jpeg)"""
    p = Path(name)
    stem = re.sub(r"[^a-z0-9._-]+", "-", p.stem.lower()).strip("-")
    return stem + p.suffix.lower()


def folder_slug(name: str):
    m = re.match(r"^(\d+)_(.+)$", name)
    return (m.group(2), int(m.group(1))) if m else (name, None)


def page_txt(folder: Path, lang: str):
    """Het inhoudsbestand (bijv. turntable.nl.txt) van een map"""
    for f in sorted(folder.glob(f"*.{lang}.txt")):
        stem = f.name[: -len(f".{lang}.txt")]
        if Path(stem).suffix.lower() in IMG_EXT:
            continue
        return f, stem
    return None, None


def images_of(folder: Path, gallery_order: list, inline: list):
    imgs = []
    for f in sorted(folder.iterdir()):
        if not f.is_file() or f.suffix.lower() not in IMG_EXT:
            continue
        meta = {lang: parse_kirby(folder / f"{f.name}.{lang}.txt") for lang in LANGS}
        if not meta["nl"]:
            meta["nl"] = parse_kirby(folder / f"{f.name}.txt")
        sort = meta["nl"].get("sort") or meta["en"].get("sort")
        imgs.append({"file": f, "name": slug_file(f.name), "orig": f.name, "meta": meta,
                     "sort": int(sort) if sort and sort.isdigit() else None})
    pos = {n: i for i, n in enumerate(gallery_order)}
    imgs.sort(key=lambda i: (i["sort"] is None, i["sort"] or 0, pos.get(i["orig"], 999), i["orig"].lower()))
    return imgs


# ── Schrijven ───────────────────────────────────────────────

def dump(fm: dict, body: str) -> str:
    fm = {k: v for k, v in fm.items() if v not in (None, "", [], {})}
    y = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000).strip()
    return f"---\n{y}\n---\n\n{body.strip()}\n" if body.strip() else f"---\n{y}\n---\n"


def convert(folder: Path, target: Path, kind: str, extra: dict | None = None):
    nl_file, template = page_txt(folder, "nl")
    if not nl_file:
        return None
    en_file, _ = page_txt(folder, "en")
    nl = parse_kirby(nl_file)
    en = parse_kirby(en_file) if en_file else {}

    body_nl, gallery, inline = body_of(nl)
    body_en, gallery_en, inline_en = body_of(en) if en else ("", [], [])
    body_nl, body_en = reflow(body_nl), reflow(body_en)
    gallery = gallery or gallery_en
    inline = inline + [i for i in inline_en if i not in inline]

    target.mkdir(parents=True, exist_ok=True)
    imgs = images_of(folder, gallery, inline)
    for img in imgs:
        shutil.copy2(img["file"], target / img["name"])
        stats["afbeeldingen"] += 1

    cover = (kirby_list(nl.get("cover", "")) or kirby_list(en.get("cover", "")) or [None])[0]
    names = {i["orig"]: i["name"] for i in imgs}
    if cover and cover not in names:
        cover = None
    cover = names.get(cover) if cover else None

    def caption(img, lang):
        m = img["meta"][lang]
        return strip_tags(m.get("caption", ""))

    gallery_imgs = [i for i in imgs if i["orig"] not in inline]
    if not cover and gallery_imgs:
        cover = gallery_imgs[0]["name"]

    if is_filler(body_nl):
        stats["lege_tekst"].append(str(target.relative_to(OUT)))
        body_nl = ""
    if is_filler(body_en):
        body_en = ""

    fslug, order = folder_slug(folder.name)
    fm = {
        "title": nl.get("title") or fslug,
        "slug": nl.get("slug") or None,
        "order": order,
        "listed": order is not None,
        "year": int(nl["year"]) if nl.get("year", "").isdigit() else None,
        "tags": [t for t in kirby_list(nl.get("tags", ""))],
        "subtitle": strip_tags(nl.get("subheadline") or nl.get("headline") or nl.get("description") or "") or None,
        "metaTitle": nl.get("meta-title") or None,
        "metaDescription": nl.get("meta-description") or None,
        "cover": cover or None,
        "images": [
            {k: v for k, v in {"src": i["name"], "caption": caption(i, "nl") or None,
                               "captionEn": caption(i, "en") if caption(i, "en") != caption(i, "nl") else None,
                               "alt": strip_tags(i["meta"]["nl"].get("alt", "")) or None}.items() if v}
            for i in gallery_imgs
        ],
    }
    if extra:
        fm.update(extra)
    (target / "index.md").write_text(dump(fm, body_nl), encoding="utf-8")

    if en:
        en_fm = {
            "title": en.get("title") if en.get("title") and en.get("title") != fm["title"] else None,
            "slug": en.get("slug") if en.get("slug") and en.get("slug") != (fm["slug"] or fslug) else None,
            "subtitle": strip_tags(en.get("subheadline") or en.get("headline") or en.get("description") or "") or None,
            "metaTitle": en.get("meta-title") or None,
            "metaDescription": en.get("meta-description") or None,
        }
        (target / "index.en.md").write_text(dump(en_fm, body_en if body_en != body_nl else ""), encoding="utf-8")
    else:
        stats["zonder_engels"].append(str(target.relative_to(OUT)))
    return template, nl, en


def main():
    if not SRC.exists():
        sys.exit(f"Kirby-content niet gevonden: {SRC}")
    for sub in ("sections", "items"):
        shutil.rmtree(OUT / sub, ignore_errors=True)

    for folder in sorted(p for p in SRC.iterdir() if p.is_dir()):
        key, order = folder_slug(folder.name)
        if key in SKIP_DIRS:
            continue
        nl_file, template = page_txt(folder, "nl")
        if not nl_file:
            continue
        nl = parse_kirby(nl_file)
        section = nl.get("slug") or key                      # technics-reparaties → repairs
        extra = {"order": order, "listed": order is not None}

        if template == "home":
            fields = parse_kirby(nl_file)
            def refs(name):
                return [r.replace("technics-reparaties/", "repairs/") for r in kirby_list(fields.get(name, ""))]
            def num(name, default):
                v = fields.get(name, "")
                return int(v) if v.isdigit() else default
            # De lijsten op de Kirby-homepage worden vinkjes op de items zelf (makkelijker in een CMS):
            # featuredforsale → forSale: true, de andere lijsten → uitgelicht: true.
            UITGELICHT.update(refs("featuredturntables") + refs("featuredspeakers") + refs("featuredconnections") + refs("featuredinteriors"))
            TE_KOOP.update(refs("featuredforsale"))
            extra = {}
        elif template == "contact":
            extra = {k: nl.get(k) or None for k in ("street", "zip", "location", "phone", "email")}
            extra["order"] = order
            extra["listed"] = order is not None

        convert(folder, OUT / "sections" / section, "section", extra)
        stats["secties"] += 1

        for child in sorted(p for p in folder.iterdir() if p.is_dir()):
            cslug, _ = folder_slug(child.name)
            if convert(child, OUT / "items" / section / cslug, "item"):
                stats["items"] += 1

    # Vinkjes zetten: "Te koop" (knop "Bel ons voor de prijs") en "Uitgelicht op de homepage"
    for refs_, veld in ((TE_KOOP, "forSale"), (UITGELICHT, "uitgelicht")):
        for ref in refs_:
            f = OUT / "items" / ref / "index.md"
            if f.exists():
                txt = f.read_text(encoding="utf-8")
                f.write_text(txt.replace("\nlisted:", f"\n{veld}: true\nlisted:", 1), encoding="utf-8")

    # Algemene site-gegevens
    site_nl = parse_kirby(SRC / "site.nl.txt") or parse_kirby(SRC / "site.txt")
    (OUT.parent / "data").mkdir(parents=True, exist_ok=True)
    (OUT.parent / "data" / "kirby-site.json").write_text(json.dumps(
        {"title": site_nl.get("title"), "keywords": site_nl.get("keywords"), "copyright": kirbytext(site_nl.get("copyright", ""))},
        ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(stats, indent=2, ensure_ascii=False))


main()
