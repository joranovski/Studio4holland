// @ts-check
import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://www.studio4holland.nl",
  // Adressen zonder slash aan het eind (/nl/turntables/drum-deck), net als op de oude site:
  // zo blijven alle adressen die Google kent precies gelijk. Netlify serveert drum-deck.html op /…/drum-deck.
  trailingSlash: "never",
  build: { format: "file" },
  image: {
    service: {
      entrypoint: "astro/assets/services/sharp",
      // AVIF met effort 2 is vele malen sneller dan de standaard (4) en nauwelijks groter.
      // Zo blijft de eerste build op Netlify ruim binnen de tijd; daarna komt alles uit de cache.
      config: { avif: { effort: 2 }, webp: { effort: 3 } },
    },
  },
});
