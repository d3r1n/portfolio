import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { heyApiPlugin } from '@hey-api/vite-plugin';
import { defineConfig } from 'vite';

let dev_env = 'localhost:8080';
// get the env var dev_env for the backend container openapi spec url
if (process.env.DEV_ENV === 'docker') {
	dev_env = 'backend:5000';
}

const transformer = async () => {
	// 1. Fetch the raw spec from your backend
	const response = await fetch(`http://${dev_env}/api/openapi.json`);
	const spec = await response.json();

	// 2. Preprocess every endpoint route before any code-gen tool sees it
	if (spec.paths) {
		for (const path of Object.keys(spec.paths)) {
			for (const method of Object.keys(spec.paths[path])) {
				const operation = spec.paths[path][method];

				// Grab whatever operationId exists (or fallback to an empty string)
				const currentId = operation.operationId || '';

				if (currentId) {
					// Strip the trailing HTTP method (e.g., '_get', '_post')
					let clean = currentId.replace(
						/_(get|post|put|delete|patch)$/i,
						''
					);

					// Split words on underscores and filter out duplicates
					const parts = clean.split('_');
					const uniqueParts = parts.filter(
						(part: string[], idx: number) =>
							parts.indexOf(part) === idx
					);

					// Convert to clean camelCase string
					operation.operationId = uniqueParts
						.map((word: string, i: number) =>
							i === 0
								? word.toLowerCase()
								: word.charAt(0).toUpperCase() + word.slice(1)
						)
						.join('');
				}
			}
		}
	}

	// 3. Hand the fully sanitized object layer straight into hey-api
	return spec;
};

export default defineConfig({
	plugins: [
		tailwindcss(),
		sveltekit(),
		heyApiPlugin({
			config: {
				// backend container openapi spec url
				input: await transformer(),
				// output directory for generated types
				output: {
					path: './src/lib/api',
					tsConfigPath: null
				},
				plugins: ['@hey-api/client-fetch']
			}
		})
	],
	server: {
		watch: {
			usePolling: true
		}
	}
});
