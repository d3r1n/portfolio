import svelte from 'eslint-plugin-svelte';
import prettier from 'eslint-config-prettier';
import js from '@eslint/js';
import ts from 'typescript-eslint';
import globals from 'globals';

export default [
	...js.configs.recommended,
	// Base TypeScript recommended rules
	...ts.configs.recommended,
	// Svelte recommended rules
	...svelte.configs['flat/recommended'],
	// Prettier config (turns off conflicting rules)
	prettier,
	// Svelte + Prettier specific integration
	...svelte.configs['flat/prettier'],
	{
		languageOptions: {
			globals: {
				...globals.browser,
				...globals.node
			}
		}
	},
	{
		ignores: ['build/', '.svelte-kit/', 'dist/']
	}
];
