<script lang="ts">
	import BookWidget from '$lib/components/home/book-widget.svelte';
	import FeaturedProjects from '$lib/components/home/featured-projects.svelte';
	import MusicWidget from '$lib/components/home/music-widget.svelte';
	import Portrait from '$lib/components/home/portrait.svelte';
	import ResumeWidget from '$lib/components/home/resume-widget.svelte';
</script>

<div class="mb-8 flex flex-col gap-8">
	<Portrait />
	<div class="flex flex-row gap-4 md:flex-col">
		<MusicWidget />
		<BookWidget />
	</div>
	<FeaturedProjects limit={2} />
	<ResumeWidget />
</div>
