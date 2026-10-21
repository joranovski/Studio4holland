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

/** Volgorde en icoon van de secties in het menu. De titels komen uit de content. */
export const SECTIONS = ["speakers", "turntables", "hextech-feet", "repairs", "connections", "interiors"] as const;
export type SectionKey = (typeof SECTIONS)[number];

/** Rijen op de homepage: welke secties, en hoeveel uitgelichte items per rij */
export const HOME_RIJEN: { sectie: SectionKey; max: number }[] = [
  { sectie: "turntables", max: 3 },
  { sectie: "speakers", max: 3 },
  { sectie: "connections", max: 4 },
  { sectie: "interiors", max: 3 },
];
export const HOME_TE_KOOP_MAX = 4;

export const SECTION_ICON: Record<string, string> = {
  speakers: "speaker",
  turntables: "vinyl",
  "hextech-feet": "hex",
  repairs: "wrench",
  connections: "link",
  interiors: "chair",
  contact: "card",
};
