import { defineConfig } from "vite";
import UnoCSS from "unocss/vite";
import solidPlugin from "vite-plugin-solid";

export default defineConfig({
    plugins: [solidPlugin(), UnoCSS()],
    server: {
        port: 3000,
    },
    build: {
        target: "esnext",
    },
});
