// Vaste gegevens van Studio 4 Holland. Pas hier contactgegevens aan; ze staan dan overal goed.

export const site = {
  name: "Studio 4 Holland",
  url: "https://www.studio4holland.nl",
  owner: "Leon Riches",
  email: "info@studio4holland.com",
  // Dit nummer stond op de oude site op de knoppen en in de footer.
  // Op de contactpagina in Kirby stond nog +31 6 20 61 91 53 (niet zichtbaar op de site).
  phone: "+31 6 57 77 31 93",
  phoneHref: "tel:+31657773193",
  // WhatsApp-knoppen verschijnen pas als hier een link staat, bijv. "https://wa.me/31657773193".
  // Eerst nagaan of Leon WhatsApp op dit nummer gebruikt.
  whatsapp: undefined as string | undefined,
  street: "Corlaerstraat 5",
  zip: "3863 ZC",
  city: "Nijkerk",
  kvk: "6247811",
  btw: "NL002422012B96",
  since: 2001,
  // SEO zoals op de oude site: elke paginatitel eindigt op deze zin (bijv. "Drum draaitafel - Het beste adres voor Technics reparatie")
  titleSuffix: {
    nl: "Het beste adres voor Technics reparatie",
    en: "The best address for Technics repair",
  },
  keywords: "STUDIO4HOLLAND, SL1200, technicsfarm, repair, maintenance",
  // Standaardbeschrijving als een pagina geen eigen beschrijving en geen tekst heeft (de oude site gebruikte deze overal)
  description: {
    nl: "Voor al je reparaties aan Technics platenspelers maar ook custom made luidsprekers en platenspelers.",
    en: "For all your Technics turntable repairs, plus custom made speakers and turntables.",
  },
};

/** Alle secties met items. De titels komen uit de content. */
export const SECTIONS = ["speakers", "turntables", "hextech-feet", "repairs", "connections", "interiors"] as const;
export type SectionKey = (typeof SECTIONS)[number];

/** Het menu: eerst wat Studio 4 Holland doet, daarna de verhalen (uitklapper "Verhalen") */
export const NAV_HOOFD: SectionKey[] = ["repairs", "turntables", "speakers", "hextech-feet"];
export const NAV_VERHALEN: SectionKey[] = ["connections", "interiors"];

/** Korte namen in het menu (de lange titel uit de content staat op de pagina zelf) */
export const NAV_LABEL: Record<SectionKey, [string, string]> = {
  repairs: ["Reparaties", "Repairs"],
  turntables: ["Draaitafels", "Turntables"],
  speakers: ["Luidsprekers", "Speakers"],
  "hextech-feet": ["Hextech", "Hextech"],
  connections: ["Connecties", "Connections"],
  interiors: ["Interieur", "Interiors"],
};

/** Soorten om op te filteren, per sectie. Elk item kiest er één (veld "soort", in het beheer een keuzelijst). */
export const SOORTEN: Partial<Record<SectionKey, { id: string; naam: [string, string] }[]>> = {
  turntables: [
    { id: "kleur", naam: ["Kleur en custom", "Colour and custom"] },
    { id: "hout", naam: ["Hout en natuur", "Wood and nature"] },
    { id: "vorm", naam: ["Bijzondere vormen", "Unusual shapes"] },
    { id: "techniek", naam: ["Techniek en restauratie", "Engineering and restoration"] },
  ],
};
/** Filtertoetsen alleen bij secties met minstens zoveel items */
export const FILTER_MIN = 8;

/** De drie ingangen bovenaan de homepage: de foto komt van deze pagina's (sectie of sectie/item) */
export const INGANG_FOTO = {
  reparatie: "repairs",
  maat: "turntables/color-collection",
};

/** Rijen op de homepage: welke secties, en hoeveel uitgelichte items per rij */
export const HOME_RIJEN: { sectie: SectionKey; max: number }[] = [
  { sectie: "turntables", max: 3 },
  { sectie: "speakers", max: 3 },
  { sectie: "connections", max: 4 },
  { sectie: "interiors", max: 3 },
];

export const SECTION_ICON: Record<string, string> = {
  speakers: "speaker",
  turntables: "vinyl",
  "hextech-feet": "hex",
  repairs: "wrench",
  connections: "link",
  interiors: "chair",
  contact: "card",
};

/** Een oproep onder de sterke punten van een sectie (alleen waar het past) */
export const SECTIE_CTA: Partial<Record<SectionKey, { kop: [string, string]; tekst: [string, string]; knop: [string, string]; soort: string }>> = {
  speakers: {
    kop: ["Horen is geloven.", "Hearing is believing."],
    tekst: ["Kom luisteren in de werkplaats in Nijkerk, of laat je huidige speakers doormeten.", "Come and listen at the workshop in Nijkerk, or have your current speakers measured."],
    knop: ["Vraag een demo aan", "Ask for a demo"],
    soort: "maat",
  },
};
