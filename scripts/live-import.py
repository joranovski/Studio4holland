#!/usr/bin/env python3
"""Neemt de content mee die alleen op de live site (www.studio4holland.nl) stond, op 21 oktober 2026.

Gebruik (vanuit st4hl-astro):

    python3 scripts/live-import.py                      # alleen teksten, titels, volgorde, verwijderingen
    python3 scripts/live-import.py <map-met-live-fotos> # ook de nieuwe items en extra foto's

De fotomap heeft de indeling <sectie>/<item>/<bestand> (en home/<bestand>), zoals downloads.tsv.
Daarna: python3 scripts/seo-live.py scripts/seo-live-2026-10-21.json
"""
import re, shutil, sys
from pathlib import Path
import yaml
from markdownify import markdownify

ROOT = Path(__file__).resolve().parent.parent
C = ROOT / "src" / "content"
FOTOS = Path(sys.argv[1]) if len(sys.argv) > 1 else None


def lees(f: Path):
    if not f.exists():
        return {}, ""
    t = f.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", t, re.S)
    return (yaml.safe_load(m.group(1)) or {}, m.group(2)) if m else ({}, t)


def schrijf(f: Path, fm: dict, body: str):
    f.parent.mkdir(parents=True, exist_ok=True)
    y = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000).strip()
    body = body.strip("\n")
    f.write_text(f"---\n{y}\n---\n\n{body}\n" if body else f"---\n{y}\n---\n", encoding="utf-8")


def md(html: str) -> str:
    """HTML van de live site → Markdown, met <br> als harde enter (backslash)."""
    html = re.sub(r"<p>\s*</p>", "", html)
    m = markdownify(html, heading_style="ATX", bullets="-")
    m = re.sub(r"[ \t]+\n", "\n", m)
    m = re.sub(r"\n{3,}", "\n\n", m).strip()
    # markdownify zet een <br> om in "  \n"; maak er een backslash-enter van
    regels = m.split("\n")
    uit = []
    for i, r in enumerate(regels):
        if i + 1 < len(regels) and r.strip() and regels[i + 1].strip() and not re.match(r"^\s*[#>\-*]", r):
            r = r.rstrip() + "\\"
        uit.append(r)
    return "\n".join(uit)


def slug_file(name: str) -> str:
    p = Path(name)
    return re.sub(r"[^a-z0-9._-]+", "-", p.stem.lower()).strip("-") + p.suffix.lower()


def zet(pad: str, lang: str, **velden):
    """Velden (title, body, …) instellen in index.md of index.en.md van een item of sectie."""
    f = C / pad / ("index.md" if lang == "nl" else "index.en.md")
    fm, body = lees(f)
    for k, v in velden.items():
        if k == "body":
            body = v
        elif v is None:
            fm.pop(k, None)
        else:
            fm[k] = v
    schrijf(f, fm, body)


# ── 1. Titels die live anders zijn ─────────────────────────────
zet("sections/repairs", "nl", title="Technics Reparaties")
zet("sections/repairs", "en", title="Technics repairs and upgrades.")
zet("items/turntables/custom-230-outlet", "nl", title="custom 220v / 240v inlet")
zet("items/turntables/custom-230-outlet", "en", title="custom 220v / 240v inlet")
zet("items/speakers/speaker-yellow-touch", "en", title="Speaker Yello touch")
zet("items/repairs/eerste-reparatie", "en", title="Typical amateur attempt at a repair")
zet("items/repairs/reparatie-2", "en", title="All good audio is made in Japan right!")
zet("items/repairs/reparatie-3", "en", title="Even this can look cool again, just needs a bit love")
zet("items/repairs/reparatie-5", "en", title="Mechanical switch problems can be a cuase of problems as well. this is a common problem with earlier models.")

# ── 2. Engelse teksten die live nieuwer zijn ───────────────────
EN = {
    "sections/turntables": "<h3>Involvement</h3> <p>My involvement with the Technics SL 1200 series of turntables goes back thirty years. I had my first pair when I was just sixteen years old; I still have them. I used SL’s as a DJ for many years, and it is fair to say I got to know them very well.</p> <p>Now my enthusiasm for them has proved to be of great value to audiophiles everywhere, because what began as a hobby is now a serious business.</p> <h3>Recycled decks</h3> <p>Technics have recently announced the new models, at a price un-affordable for many. So with my refurbishment, design and improvement service, the old decks are recycled back into use for any vinyl enthusiasts.</p> <h3>Imaginative</h3> <p>More than that, by my redesigning and imaginative décor restyling of the decks, I have produced some really cool looking models.</p> <h3>Excellent standard</h3> <p>All my decks are brought to an excellent mechanical and electronic standard, no matter what condition they are in when they come into my workshop.</p> <p>There is not much I do not know about them, so faults are quickly recognised. And, with my extensive range of spare parts, I am able to do repairs at a reasonable price. This also enables me to do repairs to all other makes of turntable.</p> <h3>100% working condition</h3> <p>So if you want that valued set of decks brought back to 100% working condition, or simply to have them modified to suit your particular use, give me a call first.</p> <p>For new enthusiasts, or DJ’s and audiophiles who want to begin again, I always have a supply of original finished decks and ‘pimped’ decks ready for sale.</p> <h3>Broken decks</h3> <p>And what of those broken and ‘distressed’ decks you no longer want? I may be interested, so tell me about them first; I will pay a fair price.</p>",
    "sections/repairs": "<h2>Repairs and customization</h2> <p>Over the years we have seen all sorts of repair requirements.<br>Nothing surprises us anymore.<br><br>They live again.<br><br>When you think it's beyond repair, just call us do not dispair!</p><p>But if you want something special we also do customization, see the photos below</p>",
    "sections/interiors": "<p>For several customers I've created bespoke Interiors &amp; Furniture</p>",
    "items/speakers/several-speakers": "<p>Its true to say that everybody hears differently, so as a speaker builder I know you can never please every type of ear. But having said that - I do like the sound of maudant short drivers, especially when they are in the correct design of cabinet. </p>",
    "items/speakers/speaker-yellow-touch": "<p>As a general rule I like to test the speakers I build with a varity of music. But I do have a bit of a passion for the musical style of Yello. look under connection in the main window to see why.</p>",
    "items/speakers/surround-speakers": "<p>various styles of surround speakers can be made - to fit your room design.</p>",
    "items/turntables/custom-230-outlet": "<p>I designed this conversion plate about 25 years ago - especially handy when decks are in and out of flight case. prevents cable damage. there is also an arm pod conversion we do for the same reason - see RCA conversion section.</p>",
    "items/turntables/metal-turntable": "<p>Again this turntable uses recycled parts from a rega p1. The overal design this time was inspired by the look of our hextechfeet. The platter is also custom made for this deck. please email for futher info and price.</p>",
    "items/repairs/reparatie-2": "<p>We have an exstensive spare parts stock.</p><p>No we dont sell spare parts! </p><p>We need them for the all the repairs we do.</p>",
    "items/repairs/reparatie-3": "<p>At S4H we also do repair other types of turntable not just technics!</p><p>But the photo shows a somewhat sorry looking turntable - just like a phoenix it did rise from the ashes of its past to be a fully funtioning and pristine deck in matt black. </p>",
    "items/repairs/reparatie-5": "<p>Amplifiers is somthing else we also repair </p>",
}
for pad, html in EN.items():
    zet(pad, "en", body=md(html))

# ── 3. Live verwijderd (404) ───────────────────────────────────
for pad in ("items/speakers/bespoke-speakers", "items/turntables/turntable-red"):
    shutil.rmtree(C / pad, ignore_errors=True)

# ── 4. Nieuwe items (alleen live) ──────────────────────────────
# [sectie, slug, NL-titel, EN-titel, NL-html, EN-html, foto's, extra]
NIEUW = [
    ["speakers", "created-earlier-this-year", "Created earlier this year", None, "",
     "<p>These Speakers are built from recycled materials and drive units. Guaranteed to get you feeling the music not just hearing it.</p>",
     ["leo_2423.jpgv2.jpg"], {}],
    ["turntables", "elm-tree-deck-based-on-a-rega-p1", "Elm tree deck", None,
     "<p>Deck created by using recycled part from two turntables.</p><p>Thorens tone arm and cabling, Oem Direct drive unit. </p><p>Piece of Elm was from a tree in my parents street</p>", None,
     ["20211113_213550-2-.jpgv2.jpg", "20211115_194033-2-.jpgv2.jpg", "20211115_194041.jpgv2.jpg", "20211113_202324-2-.jpgv2.jpg"], {}],
    ["turntables", "rca-conversion-plate", "RCA conversion plate", None, "",
     "<p>This another part I designed 25 years ago for decks in and out of flight cases, but more recently it has been used by audiophiles more as a way of upgrading signal cables more easily. Plate is 4mm alloy so there is very good at stopping unwanted EMF - radio - wifi signals from disrupting the audio path. </p>",
     ["20211026_144314.jpgv2.jpg", "20211021_194722.jpgv2.jpg"], {}],
    ["turntables", "technics-mk-tree-stump-turntable", "Technics MK tree stump turntable", None, "", None,
     ["2017-05-02-11.03.05.jpgv2.jpg", "2017-04-23-13.02.12.jpgv2.jpg", "2017-04-26-10.37.59.jpgv2.jpg", "2017-04-23-13.50.45.jpgv2.jpg", "20211129_135238-2-.jpgv2.jpg", "2017-05-02-11.02.58.jpgv2.jpg"], {}],
    ["turntables", "technics-sl1200-demonstration-deck", "Technics Sl1200 demonstration Deck", None,
     "<p>This unit I built many years ago to let people see how an SL looks from the inside, believe it or not this deck will still function with a complete platter fitted. We take this to many record fairs and has been photograhed a lot.</p>", None,
     ["20211112_122912-2-.jpgv2.jpg"], {}],
    # "Just a test": wel meegenomen, maar als concept (niet op de site en niet in "Te koop")
    ["turntables", "test-for-sale", "Test for sale", None, "<p>Just a test</p>", None,
     ["highend-turntables-on-display.jpeg"], {"draft": True, "tags": ["sale"]}],
    ["turntables", "the-re-imagined-rega-p1", "The re-imagined Rega P1", None, "",
     "<p>At Studio 4 holland I am always thinking how can certain items be improved. Well when dealing with turntables, the heavier the better. In this case, rega made a pretty decent belt drive deck with a much better than average tone arm. The only thing that let it down was what they used as a main deck frame. So I consulted a friend of mine who use a water cannon cutter on a daily basis, well as you can imagine it was not long before I had a carbon copy of the MDF rega frame in 10mm thick alloy, and then of course we did the platter as well in 10mm alloy - then sat the whole thing on a set of our slightly modified Hextech feet. (there is a separete section about the design and story for these Hextech feet) - fitted with a goldring cartridge this unit now has that warm analouge sound. Unit is for sale - please enquire via the email for further details.</p>",
     ["20170317_195440-2.jpg", "20170317_195335.jpg", "20170317_195421-3.jpg"], {}],
    ["turntables", "the-very-odd-looking-turntable", "The very odd looking turntable", None, "",
     "<p>The inspiration for this deck came from all those 70's and 80's Scifi space movies, around the workshop we called it the mars lander. Needles to say it is very heavy and due to its shape does not pick up vibration from the loudspeakers. as an extra measure against Vibration it is now fitted with our Hextech feet technology. (not shown in these photos).</p><p>The drive is of course from the legendary technics SL 1200 - control is all bespoke made buttons - arm is a modified SL 1200 arm pod unit.</p><p>item is for sale - please send email if you would like to know more.</p>",
     ["20161215_202318.jpg", "20161213_140045.jpg", "20161219_141534.jpg", "20161219_141510.jpg", "20161215_202332.jpg"], {}],
    ["repairs", "pitch-fader-replacment", "Pitch fader replacment", "At S4H we have a selection of pitch fader replacement options - with zero click or no zero click.", "",
     "<p>At S4H we have a selection of fader replacement options - with zero click or no zero click.</p>",
     ["20211016_222939.jpg"], {}],
    ["repairs", "target-light-or-more-commonly-referred-to-as-the-pop-up-light", "Target light or more commonly referred to as the pop up light", None, "",
     "<p>The target light is the achilles heal of all the SL12xx series of decks. </p><p>Nowadays we can replace it with somthing a bit longer lasting,</p><p> Yes LED - and in a varity of colours.</p>",
     ["20211118_100752-2-.jpgv2.jpg", "20211125_171554-2.jpg"], {}],
    ["repairs", "they-can-all-be-brought-back-to-life", "They can all be brought back to life....", None, "",
     "<p>So this one looks like it spent its life on the bottom of the ocean flooor, well actually a beach club, pleanty of salty air will do this over time. But hey it lives again - slightly re-styled - see addtitional pictures.</p>",
     ["20190219_124621.jpg", "20190219_124631.jpg", "20181006_092138.jpg"], {}],
]

# extra foto's bij bestaande items (achteraan in de lijst)
EXTRA = {
    "turntables/custom-230-outlet": ["20181004_130309.jpg"],
    "turntables/spacepod": ["20161213_140045.jpg"],
    "repairs/reparatie-5": ["20211028_102205-2-.jpgv2.jpg"],
}

if FOTOS:
    ontbreekt = []
    for sectie, slug, t_nl, t_en, h_nl, h_en, fotos, extra in NIEUW:
        doel = C / "items" / sectie / slug
        doel.mkdir(parents=True, exist_ok=True)
        namen = []
        for f in fotos:
            bron = FOTOS / sectie / slug / f
            if bron.exists():
                shutil.copy2(bron, doel / slug_file(f))
                namen.append(slug_file(f))
            else:
                ontbreekt.append(str(bron))
        # Live was de Nederlandse tekst vaak leeg (Kirby toonde dan niets); dan de Engelse tekst ook in het Nederlands
        body_nl = md(h_nl) if h_nl else (md(h_en) if h_en else "")
        fm = {"title": t_nl, "order": 0, "listed": True, **{k: v for k, v in extra.items()}}
        if namen:
            fm["cover"] = namen[0]
            fm["images"] = [{"src": n} for n in namen]
        schrijf(doel / "index.md", fm, body_nl)
        en_fm = {"title": t_en} if t_en else {}
        body_en = md(h_en) if h_en and md(h_en) != body_nl else ""
        if en_fm or body_en:
            schrijf(doel / "index.en.md", en_fm, body_en)
    for pad, fotos in EXTRA.items():
        doel = C / "items" / pad
        fm, body = lees(doel / "index.md")
        imgs = fm.get("images") or []
        for f in fotos:
            bron = FOTOS / pad / f
            if not bron.exists():
                ontbreekt.append(str(bron)); continue
            shutil.copy2(bron, doel / slug_file(f))
            if all(i.get("src") != slug_file(f) for i in imgs):
                imgs.append({"src": slug_file(f)})
        fm["images"] = imgs
        fm.setdefault("cover", imgs[0]["src"] if imgs else None)
        schrijf(doel / "index.md", fm, body)
    # homepage: de foto bovenaan de welkomtekst is live een andere
    home = FOTOS / "home" / "20211116_123345-2.jpg"
    if home.exists():
        shutil.copy2(home, C / "sections" / "home" / "20211116_123345-2.jpg")
        for lang in ("nl", "en"):
            f = C / "sections" / "home" / ("index.md" if lang == "nl" else "index.en.md")
            fm, body = lees(f)
            body = body.replace("![](highend-turntables-on-display.jpeg)", "![](20211116_123345-2.jpg)")
            schrijf(f, fm, body)
    else:
        ontbreekt.append(str(home))
    if ontbreekt:
        print("Niet gevonden:", *ontbreekt, sep="\n  ")

# ── 5. Volgorde zoals op de live overzichten ───────────────────
VOLGORDE = {
    "speakers": ["created-earlier-this-year", "multi-bespoke-speakers", "several-speakers", "speaker-rebuild", "speaker-yellow-touch", "speakers-videoediting", "stereo-speakers", "subwoofer", "surround-speakers"],
    "turntables": ["7-inch-single", "arm-base-conversion", "audiofile-quality-conversion", "bespoke-coloring", "boomstronk-draaitafel", "color-collection", "complete-refurbishment", "custom-230-outlet", "custom-black", "custom-sl1200", "custom-tonearm", "drum-deck", "drum-turntable", "elm-tree-deck-based-on-a-rega-p1", "funky-color", "hifi-for-sale", "highend-turntables", "metal-turntable", "needle-holder", "new-york-sl", "pacman", "rca-conversion-plate", "sl-1200-mk-one", "sl1700-mk-2014", "spacepod", "technics-mk-tree-stump-turntable", "technics-sl1200-demonstration-deck", "test-for-sale", "the-re-imagined-rega-p1", "the-very-odd-looking-turntable", "vinyl-build-turntable", "white-sl", "wood-chunk", "wooden-sl"],
    "repairs": ["eerste-reparatie", "pitch-fader-replacment", "platter", "reparatie-2", "reparatie-3", "reparatie-5", "target-light-or-more-commonly-referred-to-as-the-pop-up-light", "they-can-all-be-brought-back-to-life"],
}
for sectie, slugs in VOLGORDE.items():
    for i, slug in enumerate(slugs, start=1):
        f = C / "items" / sectie / slug / "index.md"
        if f.exists():
            fm, body = lees(f)
            fm["order"] = i
            schrijf(f, fm, body)

print("Klaar.")
