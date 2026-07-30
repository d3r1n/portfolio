import { onMount } from 'svelte';

/**
 * For widgets that have nothing to show until their first fetch completes:
 * calls `fetch` immediately on mount, exposes `loading` until it resolves,
 * then re-fetches every `intervalMs` after that (e.g. book-widget,
 * music-widget).
 *
 * Weather is the odd one out — its first value is streamed in from the
 * server, so it never has a "loading" state — which is why it doesn't use
 * this hook. See weather-content.svelte.
 *
 * Must be called during component initialization, like any other rune.
 */
export function polledResource<T>(fetch: () => Promise<T>, intervalMs: number) {
	let data = $state<T | undefined>(undefined);
	let loading = $state(true);

	onMount(() => {
		async function refresh() {
			data = await fetch();
			loading = false;
		}

		refresh();
		const interval = setInterval(refresh, intervalMs);
		return () => clearInterval(interval);
	});

	return {
		get data() {
			return data;
		},
		get loading() {
			return loading;
		}
	};
}
