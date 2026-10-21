// Twee talen, allebei met een eigen map in het adres: /nl/… en /en/… (net als op de oude Kirby-site,
// zodat bestaande links en zoekresultaten blijven werken).

export type Lang = "nl" | "en";
export const LANGS: Lang[] = ["nl", "en"];

export const t = <T>(lang: Lang, nl: T, en: T): T => (lang === "en" ? en : nl);

export function langOf(url: URL | string): Lang {
  const p = typeof url === "string" ? url : url.pathname;
  return /^\/en(\/|$)/.test(p) ? "en" : "nl";
}

// Vaste woorden op de site (de rest komt uit de content)
const woorden = {
  forSale: ["Te koop", "For sale"],
  callForPrice: ["Bel ons voor de prijs", "Call us for the price"],
  mail: ["Stuur ons een e-mail", "Send us an e-mail"],
  call: ["Bel ons", "Call us"],
  eco: ["Milieubewust / recycling", "Environmentally correct / recycling"],
  readMore: ["Lees meer", "Read more"],
  more: ["Meer", "More"],
  all: ["Alles bekijken", "View all"],
  year: ["Jaar", "Year"],
  previous: ["Vorige", "Previous"],
  next: ["Volgende", "Next"],
  close: ["Sluiten", "Close"],
  photos: ["foto's", "photos"],
  openPhoto: ["Foto groot bekijken", "View photo full size"],
  backToTop: ["Terug naar boven", "Back to top"],
  skip: ["Naar de inhoud", "Skip to content"],
  menu: ["Menu", "Menu"],
  name: ["Naam", "Name"],
  email: ["E-mail", "E-mail"],
  phone: ["Telefoon", "Phone"],
  message: ["Vraag of bericht", "Enquiry or message"],
  send: ["Verzenden", "Send"],
  optional: ["optioneel", "optional"],
  notFound: ["Deze pagina bestaat niet (meer)", "This page doesn't exist (anymore)"],
  madeBy: ["Gemaakt door", "Made by"],
  otherLang: ["English", "Nederlands"],
} satisfies Record<string, [string, string]>;

export type Woord = keyof typeof woorden;
export const w = (lang: Lang, key: Woord) => woorden[key][lang === "en" ? 1 : 0];

/** Bedankpagina na het formulier */
export const thanksPath = (lang: Lang) => t(lang, "/nl/bedankt/", "/en/thanks/");
