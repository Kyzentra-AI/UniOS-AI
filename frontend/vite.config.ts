
import { defineConfig, loadEnv } from "vite";
import vinext from "vinext";
import { cloudflare } from "@cloudflare/vite-plugin";
import { imagesOptimizer } from "@vinext/cloudflare/images/images-optimizer";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const apiUrl = env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_URL || "";

  return {
    define: {
      "process.env.NEXT_PUBLIC_API_URL": JSON.stringify(apiUrl),
    },
    envPrefix: ["VITE_", "NEXT_PUBLIC_"],
    plugins: [
      vinext({
        prerender: { routes: "*" },
        images: { optimizer: imagesOptimizer() },
      }),
      cloudflare({
        viteEnvironment: {
          name: "rsc",
          childEnvironments: ["ssr"],
        },
      }),
    ],
  };
});
