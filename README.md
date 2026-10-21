# studio4holland.nl

De site van Studio 4 Holland, gebouwd met [Astro](https://astro.build) en gehost op Netlify.
Opvolger van de Kirby/PHP-site in `../st4hl`: dezelfde content en adressen, opgefrist uiterlijk in dezelfde stijl.

## Werken aan de site

Nodig: Node.js 22.12 of nieuwer (Astro staat vast op 7.3.x, net als bij createfromcore.nl).
Astro 7.4 en hoger vraagt Node 22.22; update eerst Node voordat je Astro ophoogt.

```sh
npm install      # eenmalig
npm run dev      # live voorbeeld op http://localhost:4321
npm run build    # bouwt de site in dist/ (de eerste keer duurt dit even: alle foto's worden AVIF en WebP)
```

## Waar staat wat

| Wat | Waar |
| --- | --- |
| Teksten en foto's van een sectie (Draaitafels, Luidsprekers, …) | `src/content/sections/<sectie>/index.md` (+ `index.en.md`) |
| Projecten en producten | `src/content/items/<sectie>/<naam>/index.md` (+ `index.en.md`) |
| Homepage: welkomtekst | `src/content/sections/home/index.md` |
| Homepage: "Te koop" en de uitgelichte rijen | vinkjes `forSale` en `uitgelicht` op de items |
| Contactgegevens, KVK, BTW, telefoonnummer | `src/data/site.ts` |
| Vaste woorden in beide talen (knoppen, labels) | `src/i18n.ts` |
| Kleuren, letters, maten (designtokens) | `src/styles/tokens.css` |
| Alle opmaak | `src/styles/global.css`, de draaitafel in `src/styles/deck.css` |
| Designsystem met alle bouwstenen | `/designsystem/` (niet in zoekmachines) |
| Redirects van oude adressen, headers | `netlify.toml` |
| Omzetscript vanuit Kirby | `scripts/kirby2astro.py` |

## Beheer (CMS)

Teksten en foto's bewerken kan in de browser via **/admin/** ([Sveltia CMS](https://sveltiacms.app)).
Het beheer bewerkt dezelfde Markdown-bestanden als hierboven; opslaan is een commit op GitHub, en Netlify zet het daarna automatisch live (± 2–3 minuten).
Instellingen: `public/admin/config.yml`.

Wat Leon er ziet: per sectie (Draaitafels, Luidsprekers, …) de lijst met items, en "Pagina's" voor de homepage, de intro's en contact.
Per item: titel, tekst, foto's met bijschrift (NL en EN), jaar, en de vinkjes **Te koop** en **Uitgelicht op de homepage**.
De Engelse versie zet je aan met de taalknop bovenin het bewerkscherm; leeg laten mag, dan toont de Engelse site de Nederlandse tekst.
Grote telefoonfoto's worden bij het uploaden verkleind tot 2400 px (WebP); de site maakt er zelf AVIF en WebP in de juiste maten van.

### Eenmalig inrichten

1. Maak op GitHub (gratis account) de repo **joranovski/studio4holland** aan (privé mag) en push deze map ernaar.
   Andere naam? Pas `repo` aan in `public/admin/config.yml`.
2. Koppel de repo aan een nieuw Netlify-project (build en publish komen uit `netlify.toml`).
3. Maak op GitHub een OAuth-app: *Settings → Developer settings → OAuth Apps → New*.
   Homepage: de site-URL; **Authorization callback URL: `https://api.netlify.com/auth/done`**.
4. In Netlify: *Project configuration → Security → OAuth → Install provider → GitHub*, met de Client ID en Client Secret uit stap 3.
5. Leon maakt een gratis GitHub-account; geef hem in de repo *Settings → Collaborators* schrijfrechten.
6. Leon gaat naar `https://www.studio4holland.nl/admin/` en kiest **Sign In with GitHub**.

### Lokaal proberen (zonder GitHub)

`npm run dev`, open in Chrome of Edge `http://localhost:4321/admin/` en kies **Work with Local Repository**; selecteer de map `st4hl-astro`.
Wijzigingen komen direct in je bestanden; de dev-server laat ze meteen zien. Committen doe je zelf.

## Talen

Nederlands staat onder `/nl/`, Engels onder `/en/`, net als op de oude site.
`index.md` is de Nederlandse versie en bevat alles (foto's, jaar, volgorde).
`index.en.md` bevat alleen wat in het Engels anders is: titel, eventueel een eigen adres (`slug`) en de tekst.
Ontbreekt `index.en.md`, dan toont de Engelse pagina de Nederlandse tekst (zoals Kirby deed).
Een Engels bijschrift bij een foto staat naast het Nederlandse: `captionEn` in de lijst `images`.

## Een item toevoegen

1. Maak een map `src/content/items/turntables/mijn-draaitafel/`.
2. Zet de foto's erin en een `index.md`:

```md
---
title: Mijn draaitafel
order: 30          # plek in de lijst
year: 2026
tags: [sl1200, custom]
cover: voorkant.jpg
images:
  - src: voorkant.jpg
    caption: Voorkant
    captionEn: Front
  - src: detail.jpg
---

Tekst over de draaitafel.
```

3. Optioneel `index.en.md` met `title:` en de Engelse tekst.
4. Commit en push: Netlify zet het automatisch live.

Te koop? Zet `forSale: true` erbij: de groene knop "Bel ons voor de prijs" verschijnt en het item staat in "Te koop" op de homepage.
Op de homepage in de rij van de sectie? Zet `uitgelicht: true` (hoeveel per rij: `HOME_RIJEN` in `src/data/site.ts`).
Niet in de lijsten tonen (wel bereikbaar via de link)? Zet `listed: false`.

## Foto's

Foto's staan als JPEG/PNG naast de tekst. Bij het bouwen maakt Astro er AVIF (met WebP als terugval) van in meerdere breedtes;
de browser kiest zelf het kleinste bestand dat past. Grote originelen (tot ± 2000 px) zijn prima.

## Vanuit Kirby

De content is op 21 oktober 2026 omgezet uit de lokale Kirby-repo (`../st4hl/content`).
**Let op:** de live site had op dat moment nieuwere content (ongeveer twaalf items extra, een andere homepagefoto).
Die moet nog worden toegevoegd: haal de map `content/` van de server, zet hem in `../st4hl/content` en draai

```sh
pip install pyyaml markdownify   # eenmalig
npm run kirby
```

Het script overschrijft `src/content/sections` en `src/content/items` helemaal; doe dit dus vóór je handmatig content gaat aanpassen,
of voeg de nieuwe items daarna met de hand toe.

Bekende puntjes uit de omzetting:

- Op de contactpagina in Kirby stond telefoonnummer +31 6 20 61 91 53, op de knoppen en in de footer +31 6 57 77 31 93. De nieuwe site gebruikt overal het tweede (`src/data/site.ts`).
- Het KVK-nummer in de oude footer (6247811) heeft 7 cijfers; KVK-nummers hebben er 8. Even controleren.
- "Zwarte Hextech" had alleen opvultekst ("cccccc"); die is weggelaten.
- Het contactformulier stuurde mail naar joran.aerns@protonmail.com. Bij Netlify Forms stel je de ontvanger in onder *Site configuration → Forms → Form notifications*.
