import { defineConfig } from "vite";
import path from "path";

import UnoCSS from "unocss/vite";
import solidPlugin from "vite-plugin-solid";
import { ViteToml } from "vite-plugin-toml";

export default defineConfig({
	plugins: [solidPlugin(), UnoCSS(), ViteToml()],
	server: {
		port: 3000,
	},
	build: {
		target: "esnext",
		outDir: "dist"
	},
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "./src"),
			"@root": path.resolve(__dirname, "./"),
		},
	},
});
