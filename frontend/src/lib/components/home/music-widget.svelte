<script lang="ts">
	import { Music } from '@lucide/svelte';
	import { animate, stagger } from 'animejs';
	import {
		currentlyPlayingSpotify,
		lastPlayedSpotify,
		type Track
	} from '$lib/api';
	import { polledResource } from '$lib/utils/polled-resource.svelte';

	async function fetchMusic(): Promise<Track | null> {
		const playing = await currentlyPlayingSpotify();
		if (playing.error) {
			console.error(
				'Error fetching currently-playing track:',
				playing.error
			);
		}
		if (playing.response?.status === 200 && playing.data) {
			return playing.data;
		}

		// Nothing's playing right now — fall back to the last played track.
		const last = await lastPlayedSpotify();
		if (last.error)
			console.error('Error fetching last-played track:', last.error);
		return last.response?.status === 200 ? (last.data ?? null) : null;
	}

	const music = polledResource(fetchMusic, 30_000);

	let barsContainer = $state<HTMLElement | null>(null);

	// Keeps the equalizer bars animating in sync with playback state. Reruns
	// whenever `music.data` or the bars element changes, and its return value
	// pauses the previous animation before the next run (or on unmount).
	$effect(() => {
		if (!music.data?.is_playing || !barsContainer) return;

		const bars = barsContainer.querySelectorAll('.music-bar');
		if (bars.length === 0) return;

		const animation = animate(bars, {
			height: ['4px', '12px', '4px'],
			duration: 800,
			delay: stagger(150),
			ease: 'easeInOutQuad',
			loop: true
		});
		return () => animation.pause();
	});
</script>

{#if music.loading}
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
{:else if music.data}
	<a
		href={music.data.track_url}
		target="_blank"
		rel="noopener noreferrer"
		class="outline-base-content/10 hover:bg-base-content/5 flex items-center gap-4 rounded-sm p-3 outline-2 transition"
	>
		<div
			class="tooltip tooltip-top relative h-16 w-16 shrink-0 shadow-sm transition hover:scale-105"
			data-tip={music.data.album_name}
		>
			<img
				src={music.data.album_image}
				alt={music.data.album_name}
				class="h-full w-full rounded-sm object-cover"
			/>
			{#if music.data.is_playing}
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
					class={music.data.is_playing
						? 'text-primary'
						: 'text-base-content/50'}
				/>
				<span
					class="font-heading text-base-content/50 text-xs font-medium tracking-wider uppercase"
				>
					{music.data.is_playing ? 'Currently Playing' : 'Last Played'}
				</span>
			</div>
			<div
				class="font-heading text-base-content truncate text-sm font-semibold"
			>
				{music.data.name}
			</div>
			<div class="font-body text-base-content/70 truncate text-xs">
				{music.data.artists.join(', ')}
			</div>
		</div>
	</a>
{/if}
