
import { bindings, defineConfig, defineWorker } from "cf/config";

export default defineConfig({
  worker: defineWorker({
    name: "unios-ai",
    entrypoint: "vinext/server/fetch-handler",
    compatibilityDate: "2026-10-31",
    compatibilityFlags: ["nodejs_compat"],
    assets: {
      htmlHandling: "none",
      notFoundHandling: "none",
      runWorkerFirst: ["/*", "!/_next/static/*", "!/*/_next/static/*"],
    },
    env: {
      ASSETS: bindings.assets(),
      IMAGES: bindings.images(),
      NEXT_PUBLIC_API_URL: bindings.text(
        process.env.NEXT_PUBLIC_API_URL || "https://unios-ai.onrender.com"
      ),
    },
    observability: {
      logs: {
        enabled: true,
      },
      issues: {
    enabled: false,
  },
    },
  }),
});
