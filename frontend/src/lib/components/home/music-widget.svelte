<script lang="ts">
	import { onMount } from 'svelte';
	import { Music } from '@lucide/svelte';
	import { animate, stagger } from 'animejs';
	import {
		currentlyPlayingSpotify,
		lastPlayedSpotify,
		type Track
	} from '$lib/api';

	const REFRESH_INTERVAL_MS = 30_000;

	let musicData = $state<Track | null>(null);
	let loading = $state(true);
	let barsContainer = $state<HTMLElement | null>(null);
	let animation: ReturnType<typeof animate> | null = null;

	async function fetchMusic() {
		const playing = await currentlyPlayingSpotify();
		if (playing.error)
			console.error(
				'Error fetching currently-playing track:',
				playing.error
			);

		if (playing.response?.status === 200 && playing.data) {
			musicData = playing.data;
		} else {
			const last = await lastPlayedSpotify();
			if (last.error)
				console.error('Error fetching last-played track:', last.error);
			musicData =
				last.response?.status === 200 ? (last.data ?? null) : null;
		}

		// Handle animation in a microtask to ensure DOM is updated
		queueMicrotask(() => updateAnimation());
		loading = false;
	}

	function updateAnimation() {
		if (animation) {
			animation.pause();
			animation = null;
		}

		if (musicData?.is_playing && barsContainer) {
			const bars = barsContainer.querySelectorAll('.music-bar');
			if (bars.length > 0) {
				animation = animate(bars, {
					height: ['4px', '12px', '4px'],
					duration: 800,
					delay: stagger(150),
					ease: 'easeInOutQuad',
					loop: true
				});
			}
		}
	}

	onMount(() => {
		fetchMusic();
		const interval = setInterval(fetchMusic, REFRESH_INTERVAL_MS);
		return () => {
			clearInterval(interval);
			if (animation) animation.pause();
		};
	});
</script>

{#if loading}
	<div
		class="outline-base-content/10 flex items-center gap-4 rounded-sm p-3 outline-2"
	>
		<div class="skeleton h-16 w-16 shrink-0 rounded-sm"></div>
		<div class="flex flex-1 flex-col gap-2">
			<div class="skeleton h-3 w-24"></div>
			<div class="skeleton h-4 w-3/4"></div>
			<div class="skeleton h-3 w-2/3"></div>
		</div>
	</div>
{:else if musicData}
	<a
		href={musicData.track_url}
		target="_blank"
		rel="noopener noreferrer"
		class="outline-base-content/10 hover:bg-base-content/5 flex items-center gap-4 rounded-sm p-3 outline-2 transition"
	>
		<div
			class="tooltip tooltip-top relative h-16 w-16 shrink-0 shadow-sm transition hover:scale-105"
			data-tip={musicData.album_name}
		>
			<img
				src={musicData.album_image}
				alt={musicData.album_name}
				class="h-full w-full rounded-sm object-cover"
			/>
			{#if musicData.is_playing}
				<div
					bind:this={barsContainer}
					class="absolute right-1 bottom-1 flex items-end gap-0.5 px-1 py-0.5"
				>
					<div
						class="music-bar h-1 w-1 rounded-full bg-green-600"
					></div>
					<div
						class="music-bar h-1 w-1 rounded-full bg-green-600"
					></div>
					<div
						class="music-bar h-1 w-1 rounded-full bg-green-600"
					></div>
				</div>
			{/if}
		</div>

		<div class="flex min-w-0 flex-1 flex-col gap-1">
			<div class="flex items-center gap-2">
				<Music
					size={14}
					class={musicData.is_playing
						? 'text-primary'
						: 'text-base-content/50'}
				/>
				<span
					class="font-heading text-base-content/50 text-xs font-medium tracking-wider uppercase"
				>
					{musicData.is_playing ? 'Currently Playing' : 'Last Played'}
				</span>
			</div>
			<div
				class="font-heading text-base-content truncate text-sm font-semibold"
			>
				{musicData.name}
			</div>
			<div class="font-body text-base-content/70 truncate text-xs">
				{musicData.artists.join(', ')}
			</div>
		</div>
	</a>
{/if}
