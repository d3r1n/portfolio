<script lang="ts">
	import Navbar from "@/lib/main_page/navbar.svelte";
	import ProfileCard from "@/lib/main_page/profileCard.svelte";
	import SpotifyWidget from "@/lib/main_page/spotifyWidget.svelte";
</script>

<svelte:head>
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link
		rel="preconnect"
		href="https://fonts.gstatic.com"
		crossorigin="anonymous"
	/>
	<link
		href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Noto+Sans:ital,wght@0,100..900;1,100..900&family=Noto+Serif:ital,wght@0,100..900;1,100..900&display=swap"
		rel="stylesheet"
	/>
</svelte:head>

<!-- Outside full width -->
<div class="flex flex-col items-center justify-center gap-16 max-w-full">
	<!-- Content -->
	<div class="flex flex-col items-start gap-8 w-full md:max-w-384 p-4">
		<Navbar />
		<div class="flex justify-center gap-16 w-full">
			<ProfileCard />
			<SpotifyWidget />
		</div>
	</div>
</div>
