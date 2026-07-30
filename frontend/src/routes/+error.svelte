<script lang="ts">
	import { page } from '$app/state';
</script>

<svelte:head>
	<title>{page.status} — Derin Önder Eren</title>
</svelte:head>

<div
	class="flex min-h-[50vh] flex-col items-center justify-center gap-2 text-center"
>
	<span
		class="font-heading text-base-content/50 text-xs font-medium tracking-wider uppercase"
	>
		Error {page.status}
	</span>
	<h1 class="font-heading text-base-content text-2xl font-semibold">
		{page.error?.message ?? 'Something went wrong.'}
	</h1>
	<a href="/" class="btn btn-outline btn-neutral mt-4">Back home</a>
</div>
