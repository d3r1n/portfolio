<script lang="ts">
	import climber from '$lib/assets/climber.jpg';
	import {
		GitBranch,
		Link as LinkIcon,
		Rss,
		type LucideIcon
	} from '@lucide/svelte';
	import type { CurrentLocationWeather } from '$lib/api';
	import Navbar from '../navbar.svelte';
	import WeatherWidget from './weather-widget.svelte';

	let { weather }: { weather: Promise<CurrentLocationWeather | null> } =
		$props();

	type Link = {
		url: string;
		icon: LucideIcon;
		tooltip?: string;
	};

	const links: Link[] = [
		{
			url: 'https://github.com/d3r1n',
			icon: GitBranch,
			tooltip: 'GitHub'
		},
		{
			url: 'https://linkedin.com/in/d3r1n',
			icon: LinkIcon,
			tooltip: 'LinkedIn'
		},
		{
			url: '/thoughts/rss',
			icon: Rss,
			tooltip: 'RSS Feed'
		}
	];
</script>

<div id="portrait" class="box-border grid grid-cols-3 grid-rows-4 gap-8">
	<div
		class="outline-base-300 col-span-1 row-span-full overflow-hidden rounded-sm outline-2 outline-offset-2"
	>
		<img src={climber} alt="Derin Önder Eren" class="h-full object-cover" />
	</div>

	<Navbar class="col-span-2 row-span-1" />

	<div class="col-span-2 row-span-3 flex flex-col gap-2">
		<h1 class="font-heading text-base-content text-2xl font-medium">
			Derin Önder EREN
		</h1>

		<div class="font-body text-base-content/80 flex gap-2 tracking-wide">
			<span> stoic </span>
			<span>•</span>
			<span> polymath </span>
			<span>•</span>
			<span class="text-rotate duration-12000">
				<span>
					<span> human </span>
					<span> dumb*ss </span>
					<span> student </span>
					<span> turkish </span>
					<span> lovemaxxer </span>
					<span> naturist </span>
				</span>
			</span>
		</div>

		<div class="mt-2 flex gap-4">
			{#each links as link}
				<a
					href={link.url}
					class="tooltip tooltip-top btn btn-outline btn-neutral"
					data-tip={link.tooltip}
				>
					<link.icon size={24} />
				</a>
			{/each}
		</div>

		<div class="flex flex-col gap-1">
			<p class="font-body text-base-content mt-4">
				Doloremque modi occaecati est soluta occaecati provident sint.
				Enim sed ad fuga incidunt vel sed eos. Numquam voluptatibus
				impedit numquam iusto quisquam amet.
			</p>
			<WeatherWidget {weather} />
		</div>
	</div>
</div>
