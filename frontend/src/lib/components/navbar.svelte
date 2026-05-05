<script lang="ts">
	import { page } from '$app/state';
	import { Sun, Moon } from '@lucide/svelte';
	import { animate, utils } from 'animejs';

	import { theme } from '$lib/utils/theme-toggle.svelte';

	type Page = {
		name: string;
		slug: string;
	};

	const navPages: Page[] = [
		{
			name: 'derin?',
			slug: 'derin'
		},
		{
			name: 'works',
			slug: 'works'
		},
		{
			name: 'thoughts',
			slug: 'thoughts'
		},
		{
			name: 'connect',
			slug: 'connect'
		}
	];

	const currentPage = $derived(page.url.pathname);

	let isAnimating = false; // mutex-lock

	function toggleTheme() {
		// do nothing if clicked while animating
		if (isAnimating) return;

		isAnimating = true;

		// "hide" phase
		animate('#theme-button', {
			rotateY: 90,
			scale: 0.8,
			duration: 200,
			ease: 'inQuad',
			onComplete: () => {
				// swap state
				// also swaps the icons
				theme.toggle();

				// "show" phase
				animate('#theme-button', {
					rotateY: [270, 360], // Start from the other side
					scale: 1,
					duration: 300,
					ease: 'outBack',

					onComplete: () => {
						// reset rotation for next iteration
						utils.set('#theme-button', { rotateY: 0 });
						isAnimating = false;
					}
				});
			}
		});
	}
</script>

<div id="navbar" class="font-heading flex w-full flex-row gap-8 text-xl">
	<div>
		<a href="/">derin eren</a>
	</div>

	<div>•</div>

	<div class="flex grow items-center justify-end gap-4">
		{#each navPages as navPage}
			<span>
				<a
					href={`/${navPage.slug}`}
					class={(`/${navPage.slug}` === currentPage
						? 'underline'
						: '') + ' decoration-2'}
				>
					[ {navPage.name} ]
				</a>
			</span>
		{/each}

		<button
			id="theme-button"
			onclick={() => toggleTheme()}
			class="transform-3d"
		>
			{#if theme.current === 'light'}
				<Sun />
			{:else}
				<Moon />
			{/if}
		</button>
	</div>
</div>
