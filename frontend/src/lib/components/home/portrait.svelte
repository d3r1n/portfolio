<script lang="ts">
	import cowboyBebopPic from '$lib/assets/cowboy-bebop.jpg';
	import { GitBranch, Link, Rss, type LucideIcon } from '@lucide/svelte';

	type Link = {
		url: string;
		icon: LucideIcon;
	};

	const links: Link[] = [
		{
			url: 'https://github.com/d3r1n',
			icon: GitBranch
		},
		{
			url: 'https://linkedin.com/in/d3r1n',
			icon: Link
		},
		{
			url: '/thoughts/rss',
			icon: Rss
		}
	];
</script>

<div id="portrait" class="flex items-center gap-12">
	<div
		class="outline-base-300 aspect-square overflow-hidden rounded-full outline-2 outline-offset-2"
	>
		<img src={cowboyBebopPic} alt="" class="size-36 object-cover" />
	</div>

	<div class="flex flex-col gap-2">
		<div class="font-heading text-base-content text-2xl font-medium">
			Derin Önder EREN
		</div>

		<div class="font-body text-base-content/80 flex gap-2 tracking-wide">
			<span> stoic </span>
			<span>•</span>
			<span> polymath </span>
			<span>•</span>
			<span class="text-rotate duration-8000">
				<span>
					<span> human </span>
					<span> dumb*ss </span>
					<span> student </span>
					<span> turkish </span>
					<span> lovemaxxer </span>
				</span>
			</span>
		</div>

		<div class="mt-2 flex gap-4">
			{#each links as link}
				<a href={link.url} class="btn btn-outline btn-secondary">
					<link.icon size={24} />
				</a>
			{/each}
		</div>
	</div>
</div>
