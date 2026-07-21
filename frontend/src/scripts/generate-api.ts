import { createClient } from '@hey-api/openapi-ts';
import fs from 'node:fs';
import path from 'node:path';

let dev_env = 'localhost:8080';
if (process.env.DEV_ENV === 'docker') {
	dev_env = 'backend:5000';
}

const LOCAL_SPEC_PATH = path.resolve('./openapi.json');

// 1. Transform raw spec object
function transformSpec(spec: any) {
	if (!spec.paths) return spec;

	for (const pathKey of Object.keys(spec.paths)) {
		for (const method of Object.keys(spec.paths[pathKey])) {
			const operation = spec.paths[pathKey][method];
			const currentId = operation.operationId || '';

			if (currentId) {
				// Strip trailing HTTP method
				const clean = currentId.replace(
					/_(get|post|put|delete|patch)$/i,
					''
				);

				// Deduplicate parts
				const parts = clean.split('_');
				const uniqueParts = parts.filter(
					(part: string, idx: number) => parts.indexOf(part) === idx
				);

				// Convert to camelCase
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
	return spec;
}

async function run() {
	let spec: any;

	try {
		console.log(
			`📡 Fetching OpenAPI spec from http://${dev_env}/api/openapi.json...`
		);
		const response = await fetch(`http://${dev_env}/api/openapi.json`);

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}

		spec = await response.json();

		// Cache a local copy for offline dev/fallback
		fs.writeFileSync(LOCAL_SPEC_PATH, JSON.stringify(spec, null, 2));
		console.log('💾 Saved latest openapi.json locally.');
	} catch (err: any) {
		console.warn(`⚠️ Could not reach backend (${err.message}).`);

		if (fs.existsSync(LOCAL_SPEC_PATH)) {
			console.log('🔄 Falling back to local openapi.json...');
			spec = JSON.parse(fs.readFileSync(LOCAL_SPEC_PATH, 'utf-8'));
		} else {
			console.error(
				'❌ No local openapi.json fallback found. Aborting codegen.'
			);
			process.exit(1);
		}
	}

	// 2. Transform the spec
	const cleanedSpec = transformSpec(spec);

	// 3. Generate client code
	await createClient({
		input: cleanedSpec,
		output: {
			path: './src/lib/api',
			tsConfigPath: null
		},
		plugins: ['@hey-api/client-fetch']
	});

	console.log('✨ Client generated successfully in ./src/lib/api');
}

run();
