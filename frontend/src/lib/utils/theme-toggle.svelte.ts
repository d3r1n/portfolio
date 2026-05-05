import { browser } from '$app/environment';

class ThemeStore {
	// Initialize from localStorage if in browser, otherwise default to light
	current = $state<'light' | 'dark'>(
		(browser && (localStorage.getItem('theme') as 'light' | 'dark')) || 'light'
	);

	private themes = {
		light: 'wireframe',
		dark: 'business'
	};

	constructor() {
		// Sync to localStorage whenever 'current' changes
		$effect.root(() => {
			$effect(() => {
				if (browser) {
					localStorage.setItem('theme', this.current);
					document.documentElement.setAttribute(
						'data-theme',
						this.themes[this.current]
					);
				}
			});
		});
	}

	toggle() {
		this.current = this.current === 'light' ? 'dark' : 'light';
	}
}

export const theme = new ThemeStore();
