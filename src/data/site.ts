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
  keywords: "Studio 4 Holland, Technics, SL1200, SL1210, draaitafel reparatie, turntable repair, customization, speakers",
  description: {
    nl: "Studio 4 Holland in Nijkerk: reparatie, onderhoud en customizing van Technics-draaitafels, luidsprekers op maat, Hextech-voetjes en interieurs.",
    en: "Studio 4 Holland in Nijkerk, the Netherlands: Technics turntable repair, maintenance and customisation, bespoke speakers, Hextech feet and interiors.",
  },
};

/** Volgorde en icoon van de secties in het menu. De titels komen uit de content. */
export const SECTIONS = ["speakers", "turntables", "hextech-feet", "repairs", "connections", "interiors"] as const;
export type SectionKey = (typeof SECTIONS)[number];

export const SECTION_ICON: Record<string, string> = {
  speakers: "speaker",
  turntables: "vinyl",
  "hextech-feet": "hex",
  repairs: "wrench",
  connections: "link",
  interiors: "chair",
  contact: "card",
};
