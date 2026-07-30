<script lang="ts">
	import { onMount } from 'svelte';
	import {
		CloudLightning,
		CloudDrizzle,
		CloudRain,
		CloudSnow,
		CloudFog,
		Cloud,
		CloudSun,
		CloudMoon,
		Sun,
		Moon,
		MapPin,
		Clock,
		type Icon as IconType
	} from '@lucide/svelte';
	import {
		currentLocationAndWeather,
		type CurrentLocationWeather
	} from '$lib/api';

	const REFRESH_INTERVAL_MS = 60_000;

	// The first value comes from the server (weather-widget.svelte streams it
	// in). We keep it in our own $state so `data` can be replaced whenever a
	// poll comes back.
	let { initial }: { initial: CurrentLocationWeather | null } = $props();
	// svelte-ignore state_referenced_locally
	let data = $state(initial);

	onMount(() => {
		const interval = setInterval(async () => {
			const { data: freshData, error } =
				await currentLocationAndWeather();
			if (error) console.error('Error fetching weather data:', error);
			data = freshData ?? null;
		}, REFRESH_INTERVAL_MS);

		return () => clearInterval(interval);
	});

	// `data.weather` is the actual reading (temperature, sky, ...) — pulled
	// out once so the rest of this file doesn't have to keep writing
	// `data?.weather?.x`.
	const condition = $derived(data?.weather);

	// A reading's `dt` (when it was taken, in UTC seconds) plus `timezone`
	// (that location's UTC offset, also in seconds) gives us the site owner's
	// local date/time — independent of whatever timezone the visitor is in.
	const localDate = $derived(
		condition ? new Date((condition.dt + condition.timezone) * 1000) : null
	);

	const localTime = $derived(
		localDate?.toLocaleTimeString('en-GB', {
			hour: '2-digit',
			minute: '2-digit',
			timeZone: 'UTC'
		}) ?? null
	);

	// OpenWeatherMap doesn't tell us day vs. night, so we guess from the local
	// hour instead: treat 8pm-6am as night.
	const isNight = $derived(
		localDate != null &&
			(localDate.getUTCHours() < 6 || localDate.getUTCHours() >= 20)
	);

	const WeatherIcon = $derived(
		condition ? iconFor(condition.weather_id, isNight) : Cloud
	);

	// OpenWeatherMap groups its condition codes by leading digit: 2xx storm,
	// 3xx drizzle, 5xx rain, 6xx snow, 7xx atmosphere (fog/haze/etc), 800
	// clear, 801-804 clouds.
	function iconFor(weatherId: number, isNight: boolean): typeof IconType {
		switch (Math.floor(weatherId / 100)) {
			case 2:
				return CloudLightning;
			case 3:
				return CloudDrizzle;
			case 5:
				return CloudRain;
			case 6:
				return CloudSnow;
			case 7:
				return CloudFog;
			case 8:
				if (weatherId === 800) return isNight ? Moon : Sun;
				return isNight ? CloudMoon : CloudSun;
			default:
				return Cloud;
		}
	}
</script>

{#if data}
	<div
		class="font-body text-base-content/50 flex flex-wrap items-center gap-4 text-xs"
	>
		<span class="flex items-center gap-2">
			<MapPin size={12} class="inline-block" />
			{data.location_name}
		</span>

		{#if localTime}
			<span class="flex items-center gap-2">
				<Clock size={12} class="inline-block" />
				{localTime}
			</span>
		{/if}

		{#if condition}
			<span
				class="tooltip tooltip-top flex items-center gap-2 capitalize"
				data-tip={condition.description}
			>
				<WeatherIcon size={12} class="inline-block" />
				{Math.round(condition.temperature)}°C
			</span>
		{/if}
	</div>
{:else}
	<div
		class="outline-base-content/10 flex items-center gap-3 rounded-sm p-3 outline-2"
	>
		<MapPin size={16} class="text-base-content/50" />
		<div class="font-body text-base-content/60 text-sm">
			Location unavailable.
		</div>
	</div>
{/if}
