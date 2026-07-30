<script lang="ts">
	import { BookOpen } from '@lucide/svelte';
	import { currentlyReadingBooks, type HardcoverBook } from '$lib/api';
	import { polledResource } from '$lib/utils/polled-resource.svelte';

	async function fetchBook(): Promise<HardcoverBook | null> {
		const { data, error, response } = await currentlyReadingBooks();
		if (error) console.error('Error fetching book data:', error);

		// A 204 means there's simply no active book right now — not an error.
		return response?.status === 200 ? (data ?? null) : null;
	}

	const book = polledResource(fetchBook, 60_000);
</script>

{#if book.loading}
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
{:else if book.data}
	<a
		href={book.data.link}
		target="_blank"
		rel="noopener noreferrer"
		class="outline-base-content/10 hover:bg-base-content/5 flex gap-4 rounded-sm p-3 outline-2 transition"
	>
		<div
			class="relative aspect-2/3 shrink-0 overflow-hidden rounded-sm shadow-sm transition hover:scale-105"
			style={book.data.image_dominant_color
				? `background-color: ${book.data.image_dominant_color};`
				: undefined}
		>
			{#if book.data.image_url}
				<img
					src={book.data.image_url}
					alt={book.data.title}
					class="absolute inset-0 h-full w-full object-cover"
				/>
			{:else}
				<div
					class="bg-base-content/10 absolute inset-0 flex items-center justify-center"
				>
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
				{book.data.title}
			</div>
			<div class="font-body text-base-content/70 truncate text-xs">
				{book.data.author}
				{#if book.data.pages !== null && book.data.pages !== undefined}
					<span class="text-base-content/50">
						• {book.data.pages} pages</span
					>
				{/if}
			</div>

			{#if book.data.progress !== null && book.data.progress !== undefined}
				<div class="mt-1 flex items-center gap-2">
					<progress
						class="progress progress-neutral h-1.5 w-full"
						value={book.data.progress}
						max="100"
					></progress>
					<span
						class="font-body text-base-content/50 w-9 text-[10px]"
					>
						{Math.round(book.data.progress)}%
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
