// Alles wat pagina's nodig hebben uit de content: Nederlands als basis, Engels eroverheen.
import { getCollection, getEntry, render, type CollectionEntry } from "astro:content";
import type { ImageMetadata } from "astro";
import { SECTIONS } from "../data/site";
import type { Lang } from "../i18n";

type Nl = CollectionEntry<"sections"> | CollectionEntry<"items">;
type En = CollectionEntry<"sectionsEn"> | CollectionEntry<"itemsEn">;

export interface Photo {
  src: ImageMetadata;
  caption?: string;
  alt: string;
}

export interface Page {
  id: string;
  kind: "section" | "item";
  /** sectie waar het item onder valt (of de sectie zelf) */
  section: string;
  lang: Lang;
  title: string;
  subtitle?: string;
  /** citaat voor de kantlijn van een verhaal */
  citaat?: string;
  /** aantal woorden in de tekst (lange teksten krijgen de tijdschriftopmaak) */
  woorden: number;
  slug: string;
  url: string;
  /** hetzelfde adres in de andere taal */
  alt: Record<Lang, string>;
  year?: number;
  tags: string[];
  order: number;
  listed: boolean;
  forSale: boolean;
  uitgelicht: boolean;
  /** soort binnen de sectie (filtertoetsen) */
  soort?: string;
  metaTitle?: string;
  metaDescription?: string;
  cover?: ImageMetadata;
  photos: Photo[];
  excerpt: string;
  /** of er Engelse tekst is (anders tonen we de Nederlandse) */
  translated: boolean;
  nl: Nl;
  en?: En;
}

/** Eerste ~160 tekens platte tekst, voor kaartjes en de meta-description */
export function excerptOf(body = "", max = 160) {
  const plain = body
    .replace(/!\[[^\]]*\]\([^)]*\)/g, "")
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/^#{1,6}\s+.*$/gm, "")
    .replace(/^[>\-*]\s*/gm, "")
    .replace(/\\$/gm, "")
    .replace(/[*_`\\]/g, "")
    .replace(/\s+/g, " ")
    .trim();
  return plain.length > max ? plain.slice(0, plain.lastIndexOf(" ", max)) + " …" : plain;
}

const slugOf = (id: string, own?: string) => own || id.split("/").pop()!;

function build(kind: Page["kind"], nl: Nl, en: En | undefined, lang: Lang): Page {
  const section = kind === "section" ? nl.id : nl.id.split("/")[0];
  const nlSlug = slugOf(nl.id, nl.data.slug);
  const enSlug = slugOf(nl.id, en?.data.slug ?? nl.data.slug);
  const path = (l: Lang) => {
    const s = l === "en" ? enSlug : nlSlug;
    // Zonder slash aan het eind, precies zoals de adressen op de oude Kirby-site (goed voor de vindbaarheid)
    if (kind === "section") return section === "home" ? `/${l}` : `/${l}/${s}`;
    return `/${l}/${section}/${s}`;
  };
  const useEn = lang === "en" && en;
  const d = nl.data;
  const title = (useEn && en!.data.title) || d.title;
  const body = (useEn && en!.body?.trim()) ? en!.body : nl.body;
  return {
    id: nl.id,
    kind,
    section,
    lang,
    title,
    subtitle: (useEn && en!.data.subtitle) || d.subtitle,
    citaat: (useEn && en!.data.citaat) || d.citaat,
    woorden: (body ?? "").split(/\s+/).filter(Boolean).length,
    slug: lang === "en" ? enSlug : nlSlug,
    url: path(lang),
    alt: { nl: path("nl"), en: path("en") },
    year: d.year,
    tags: d.tags ?? [],
    order: d.order ?? 999,
    listed: d.listed,
    forSale: !!d.forSale || (d.tags ?? []).some((t) => /^(sale|te koop)$/i.test(t)),
    uitgelicht: !!d.uitgelicht,
    soort: d.soort,
    metaTitle: (useEn && en!.data.metaTitle) || (lang === "nl" ? d.metaTitle : undefined),
    metaDescription: (useEn && en!.data.metaDescription) || (lang === "nl" ? d.metaDescription : undefined),
    cover: d.cover,
    photos: (d.images ?? []).map((i) => {
      const caption = (lang === "en" && i.captionEn) || i.caption;
      return { src: i.src, caption, alt: i.alt || caption || title };
    }),
    excerpt: excerptOf(body ?? ""),
    translated: lang === "nl" || !!(en && (en.body?.trim() || en.data.title)),
    nl,
    en,
  };
}

let cache: { sections: CollectionEntry<"sections">[]; items: CollectionEntry<"items">[]; sEn: Map<string, En>; iEn: Map<string, En> } | undefined;
async function load() {
  if (!cache) {
    const [sections, items, sEn, iEn] = await Promise.all([
      getCollection("sections", (e) => !e.data.draft),
      getCollection("items", (e) => !e.data.draft),
      getCollection("sectionsEn"),
      getCollection("itemsEn"),
    ]);
    cache = { sections, items, sEn: new Map(sEn.map((e) => [e.id, e])), iEn: new Map(iEn.map((e) => [e.id, e])) };
  }
  return cache;
}

export async function getSection(id: string, lang: Lang) {
  const c = await load();
  const nl = c.sections.find((s) => s.id === id);
  return nl ? build("section", nl, c.sEn.get(id), lang) : undefined;
}

/** Secties voor het menu, in de vaste volgorde */
export async function getNav(lang: Lang) {
  const all = await Promise.all(SECTIONS.map((s) => getSection(s, lang)));
  return all.filter((s): s is Page => !!s);
}

/** Items van een sectie, op volgorde; standaard alleen de zichtbare */
export async function getItems(section: string, lang: Lang, { all = false } = {}) {
  const c = await load();
  return c.items
    .filter((e) => e.id.startsWith(section + "/") && (all || e.data.listed))
    .map((e) => build("item", e, c.iEn.get(e.id), lang))
    .sort((a, b) => a.order - b.order || a.title.localeCompare(b.title));
}

/** Uitgelichte items van een sectie voor de homepage (vinkje "Uitgelicht op de homepage") */
export async function getUitgelicht(section: string, lang: Lang, max: number) {
  return (await getItems(section, lang)).filter((i) => i.uitgelicht).slice(0, max);
}

/** Alles met het vinkje "Te koop", uit alle secties */
export async function getTeKoop(lang: Lang, max = 99) {
  const lijsten = await Promise.all(SECTIONS.map((s) => getItems(s, lang)));
  return lijsten.flat().filter((i) => i.forSale).slice(0, max);
}

export async function renderBody(p: Page) {
  const useEn = p.lang === "en" && p.en?.body?.trim();
  return render((useEn ? p.en : p.nl) as Nl);
}

// ── paden voor getStaticPaths ───────────────────────────────

export async function sectionPaths(lang: Lang) {
  const secs = await getNav(lang);
  return secs.map((page) => ({ params: { section: page.slug }, props: { page } }));
}

export async function itemPaths(lang: Lang) {
  const out = [];
  for (const s of SECTIONS) {
    const sec = await getSection(s, lang);
    if (!sec) continue;
    const items = await getItems(s, lang, { all: true });
    const listed = items.filter((i) => i.listed);
    for (const page of items) {
      const i = listed.indexOf(page);
      out.push({
        params: { section: sec.slug, slug: page.slug },
        props: {
          page,
          sectionPage: sec,
          prev: i > 0 ? listed[i - 1] : undefined,
          next: i >= 0 && i < listed.length - 1 ? listed[i + 1] : undefined,
          // plek in de lijst, voor de teller ("08 / 33") op de telefoon
          pos: i >= 0 ? i + 1 : undefined,
          totaal: listed.length,
        },
      });
    }
  }
  return out;
}

export { getEntry };
