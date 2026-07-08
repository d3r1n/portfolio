<script lang="ts">
	import { onMount } from 'svelte';
	import { BookOpen } from '@lucide/svelte';
	import {
		getCurrentlyReadingBook,
		type HardcoverBook
	} from '$lib/api/client';

	let bookData = $state<HardcoverBook | null>(null);
	let loading = $state(true);

	async function fetchBook() {
		try {
			bookData = await getCurrentlyReadingBook();
		} catch (error) {
			console.error('Error fetching book data:', error);
			bookData = null;
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		fetchBook();
		const interval = setInterval(fetchBook, 60000);
		return () => clearInterval(interval);
	});
</script>

{#if loading}
	<div
		class="outline-base-content/10 flex items-center gap-4 rounded-sm p-3 outline-2"
	>
		<div class="skeleton h-16 w-12 shrink-0 rounded-sm"></div>
		<div class="flex flex-1 flex-col gap-2">
			<div class="skeleton h-3 w-24"></div>
			<div class="skeleton h-4 w-3/4"></div>
			<div class="skeleton h-3 w-2/3"></div>
		</div>
	</div>
{:else if bookData}
	<a
		href={bookData.link}
		target="_blank"
		rel="noopener noreferrer"
		class="outline-base-content/10 hover:bg-base-content/5 flex items-center gap-4 rounded-sm p-3 outline-2 transition"
	>
		<div
			class="relative h-16 w-12 shrink-0 overflow-hidden rounded-sm shadow-sm transition hover:scale-105"
			style={bookData.image_dominant_color
				? `background-color: ${bookData.image_dominant_color};`
				: undefined}
		>
			{#if bookData.image_url}
				<img
					src={bookData.image_url}
					alt={bookData.title}
					class="h-full w-full object-cover"
				/>
			{:else}
				<div class="bg-base-content/10 flex h-full w-full items-center justify-center">
					<BookOpen size={16} class="text-base-content/50" />
				</div>
			{/if}
		</div>

		<div class="flex min-w-0 flex-1 flex-col gap-1">
			<div class="flex items-center gap-2">
				<BookOpen size={14} class="text-primary" />
				<span
					class="font-heading text-base-content/50 text-xs font-medium tracking-wider uppercase"
				>
					Currently reading
				</span>
			</div>
			<div
				class="font-heading text-base-content truncate text-sm font-semibold"
			>
				{bookData.title}
			</div>
			<div class="font-body text-base-content/70 truncate text-xs">
				{bookData.author}
				{#if bookData.pages !== null && bookData.pages !== undefined}
					<span class="text-base-content/50"> • {bookData.pages} pages</span>
				{/if}
			</div>

			{#if bookData.progress !== null && bookData.progress !== undefined}
				<div class="mt-1 flex items-center gap-2">
					<progress
						class="progress progress-neutral h-1.5 w-full"
						value={bookData.progress}
						max="100"
					></progress>
					<span class="font-body text-base-content/50 w-9 text-[10px]">
						{Math.round(bookData.progress)}%
					</span>
				</div>
			{/if}
		</div>
	</a>
{:else}
	<div
		class="outline-base-content/10 flex items-center gap-3 rounded-sm p-3 outline-2"
	>
		<BookOpen size={16} class="text-base-content/50" />
		<div class="font-body text-base-content/60 text-sm">
			No current book yet.
		</div>
	</div>
{/if}