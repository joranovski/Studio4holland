#!/usr/bin/env python3
"""Zet de SEO-titels en -beschrijvingen van de oude live site in de content (metaTitle / metaDescription).

Gebruik (vanuit de map st4hl-astro), na een import met kirby2astro.py:

    python3 scripts/seo-live.py scripts/seo-live-2026-10-21.json

Het JSON-bestand is op 21 oktober 2026 van www.studio4holland.nl gehaald: per adres
[titel zonder de vaste zin, metatitel, metabeschrijving]. Alleen wat afwijkt van wat de nieuwe
site uit zichzelf zou tonen, wordt opgeslagen. Pagina's die alleen live bestaan, worden gemeld.
"""
import json, re, sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
C = ROOT / "src" / "content"


def lees(f: Path):
    if not f.exists():
        return {}, ""
    t = f.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", t, re.S)
    return (yaml.safe_load(m.group(1)) or {}, m.group(2)) if m else ({}, t)


def schrijf(f: Path, fm: dict, body: str):
    y = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000).strip()
    body = body.strip("\n")
    f.write_text(f"---\n{y}\n---\n\n{body}\n" if body else f"---\n{y}\n---\n", encoding="utf-8")


norm = lambda s: re.sub(r"\s+", " ", s or "").strip()

# adres → map
adressen = {}
for basis, soort in ((C / "sections", "sectie"), (C / "items", "item")):
    for nl in basis.rglob("index.md"):
        map_ = nl.parent
        fm, _ = lees(nl)
        fm_en, _ = lees(map_ / "index.en.md")
        naam = map_.name
        for lang, slug in (("nl", fm.get("slug") or naam), ("en", fm_en.get("slug") or fm.get("slug") or naam)):
            if soort == "sectie":
                pad = f"/{lang}" if naam == "home" else f"/{lang}/{slug}"
            else:
                pad = f"/{lang}/{map_.parent.name}/{slug}"
            adressen[pad] = (map_, lang)

live = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
gewijzigd, alleen_live = 0, []
for pad, (titel, _metatitel, beschrijving) in live.items():
    if pad not in adressen:
        alleen_live.append(pad)
        continue
    map_, lang = adressen[pad]
    f = map_ / ("index.md" if lang == "nl" else "index.en.md")
    fm, body = lees(f)
    fm_nl, _ = lees(map_ / "index.md")
    toon = norm(fm.get("title") or fm_nl.get("title"))
    nieuw = dict(fm)
    # De live site is leidend: wat Google nu kent, overschrijft oudere lokale SEO-velden
    if norm(titel) and norm(titel) != toon:
        nieuw["metaTitle"] = norm(titel)
    elif norm(titel) == toon:
        nieuw.pop("metaTitle", None)
    if norm(beschrijving):
        nieuw["metaDescription"] = norm(beschrijving)
    if nieuw != fm:
        schrijf(f, nieuw, body)
        gewijzigd += 1

print(f"{gewijzigd} bestanden bijgewerkt")
print(f"{len(alleen_live)} adressen bestaan alleen op de live site (nog toevoegen):")
for p in alleen_live:
    print("  ", p)
