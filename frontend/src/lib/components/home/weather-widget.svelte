<script lang="ts">
	import type { CurrentLocationWeather } from '$lib/api';
	import WeatherContent from './weather-content.svelte';

	// +page.server.ts streams weather in as a promise instead of awaiting it,
	// so the rest of the page doesn't wait on this slow upstream call.
	// {#await} is how a template waits on that promise — but it can't hold
	// state that changes afterwards, and we need that for polling. So this
	// component only resolves the promise; WeatherContent (a real component,
	// with real $state) takes it from there.
	let { weather }: { weather: Promise<CurrentLocationWeather | null> } =
		$props();
</script>

{#await weather}
	<div class="flex items-center gap-4">
		<div class="skeleton h-3 w-32"></div>
		<div class="skeleton h-3 w-16"></div>
		<div class="skeleton h-3 w-12"></div>
	</div>
{:then initialWeather}
	<WeatherContent initial={initialWeather} />
{/await}
