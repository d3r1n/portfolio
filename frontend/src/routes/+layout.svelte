<script lang="ts">
	import '../styles/app.css';
	import favicon from '$lib/assets/favicon.svg';
	import Navbar from '$lib/components/navbar.svelte';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />

	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link
		rel="preconnect"
		href="https://fonts.gstatic.com"
		crossorigin="anonymous"
	/>
	<link
		href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400..700;1,400..700&family=Roboto:ital,wdth,wght@0,75..100,100..900;1,75..100,100..900&display=swap"
		rel="stylesheet"
	/>
</svelte:head>

<div id="viewport-container" class="flex w-screen justify-center">
	<div id="content" class="w-[60%] pt-48">
		<Navbar />
		{@render children()}
	</div>
</div>
