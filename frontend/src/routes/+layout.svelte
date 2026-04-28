<script lang="ts">
	import '../styles/app.css';
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<div id="viewport-container" class="flex w-screen justify-center">
	<div id="content" class="w-[60%] pt-48">
		{@render children()}
	</div>
</div>
