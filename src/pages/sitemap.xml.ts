// Sitemap voor zoekmachines: alle pagina's in het Nederlands en het Engels, elk met zijn tegenhanger (hreflang).
// Nieuwe items komen er vanzelf in.
import type { APIRoute } from "astro";
import { getNav, getSection, getItems } from "../lib/content";
import { SECTIONS } from "../data/site";

export const GET: APIRoute = async ({ site }) => {
  const paren: { nl: string; en: string }[] = [];
  for (const id of ["home", "contact"]) {
    const s = await getSection(id, "nl");
    if (s) paren.push(id === "contact" ? { nl: "/nl/contact", en: "/en/contact" } : s.alt);
  }
  for (const s of await getNav("nl")) paren.push(s.alt);
  for (const sec of SECTIONS) for (const i of await getItems(sec, "nl")) paren.push(i.alt);
  const url = (u: string) => new URL(u, site).href;
  const regels = paren.flatMap((p) => {
    const alt = `<xhtml:link rel="alternate" hreflang="nl" href="${url(p.nl)}"/><xhtml:link rel="alternate" hreflang="en" href="${url(p.en)}"/><xhtml:link rel="alternate" hreflang="x-default" href="${url(p.nl)}"/>`;
    return [p.nl, p.en].map((u) => `  <url><loc>${url(u)}</loc>${alt}</url>`);
  });
  return new Response(
    `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n${regels.join("\n")}\n</urlset>\n`,
    { headers: { "Content-Type": "application/xml; charset=utf-8" } },
  );
};
