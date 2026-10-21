import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";
import { z } from "astro/zod";

// Eén map per pagina: index.md (Nederlands, volledig) en eventueel index.en.md (alleen wat in het Engels anders is).
// Afbeeldingen staan naast de Markdown; Astro maakt er bij het bouwen AVIF en WebP van.

const beeld = (image: () => z.ZodTypeAny) =>
  z.object({
    src: image(),
    caption: z.string().optional(),
    /** Engels bijschrift, als het anders is dan het Nederlandse */
    captionEn: z.string().optional(),
    alt: z.string().optional(),
  });

const nlSchema = ({ image }: { image: () => z.ZodTypeAny }) =>
  z.object({
    title: z.string(),
    /** eigen adres in plaats van de mapnaam */
    slug: z.string().optional(),
    order: z.number().optional(),
    /** false = niet in lijsten en menu (wel bereikbaar via de link) */
    listed: z.boolean().default(true),
    draft: z.boolean().optional(),
    year: z.number().optional(),
    tags: z.array(z.string()).optional(),
    subtitle: z.string().optional(),
    metaTitle: z.string().optional(),
    metaDescription: z.string().optional(),
    /** te koop: toont "Bel ons voor de prijs" en staat in "Te koop" op de homepage */
    forSale: z.boolean().optional(),
    /** uitgelicht in de rij van deze sectie op de homepage */
    uitgelicht: z.boolean().optional(),
    cover: image().optional(),
    images: z.array(beeld(image)).optional(),
    // alleen op de contactpagina
    street: z.string().optional(),
    zip: z.string().optional(),
    location: z.string().optional(),
    phone: z.string().optional(),
    email: z.string().optional(),
  });

const enSchema = z.object({
  title: z.string().optional(),
  slug: z.string().optional(),
  subtitle: z.string().optional(),
  metaTitle: z.string().optional(),
  metaDescription: z.string().optional(),
});

const id = (suffix: string) => ({ entry }: { entry: string }) => entry.replace(suffix, "");

/** Secties: home, speakers, turntables, hextech-feet, repairs, connections, interiors, contact */
const sections = defineCollection({
  loader: glob({ pattern: "*/index.md", base: "./src/content/sections", generateId: id("/index.md") }),
  schema: nlSchema,
});
const sectionsEn = defineCollection({
  loader: glob({ pattern: "*/index.en.md", base: "./src/content/sections", generateId: id("/index.en.md") }),
  schema: enSchema,
});

/** Items binnen een sectie: items/<sectie>/<naam>/index.md → id "turntables/drum-deck" */
const items = defineCollection({
  loader: glob({ pattern: "*/*/index.md", base: "./src/content/items", generateId: id("/index.md") }),
  schema: nlSchema,
});
const itemsEn = defineCollection({
  loader: glob({ pattern: "*/*/index.en.md", base: "./src/content/items", generateId: id("/index.en.md") }),
  schema: enSchema,
});

export const collections = { sections, sectionsEn, items, itemsEn };
