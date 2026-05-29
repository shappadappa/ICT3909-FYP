// @ts-check
import { defineConfig } from "astro/config";

import tailwindcss from "@tailwindcss/vite";

import react from "@astrojs/react";

import vercel from "@astrojs/vercel";

// https://astro.build/config
export default defineConfig({
	vite: {
		plugins: [tailwindcss()],
	},
	server: {
		port: 3000,
	},
	integrations: [react()],
	adapter: vercel(),
	security: {
		checkOrigin: false,
	},
	output: "server",
});
