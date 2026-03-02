<script lang="ts">
	import { Github, Link, Linkedin } from "@lucide/svelte";
	import DevdottoIcon from "./misc/DevdottoIcon.svelte";

	const socialLinks = [
		{ icon: Github, link: "https://github.com/d3r1n" },
		{ icon: Linkedin, link: "https://linkedin.com/in/d3r1n" },
		{ icon: DevdottoIcon, link: "https://dev.to/d3r1n" },
	];
</script>

<div
	id="profile-card"
	class="flex gap-8 items-center p-8 rounded-sm font-[Inter] shadow-sm dark:shadow-none dark:outline-2 outline-base-content/10 w-full"
>
	<div class="avatar">
		<div
			class="w-64 rounded-full ring-2 ring-accent ring-offset-2 ring-offset-base-100"
		>
			<img src="/profile-pic.jpg" alt="profile" />
		</div>
	</div>

	<div class="flex flex-col justify-center items-center gap-4">
		<span class="text-4xl font-semibold text-base-content">
			Derin Önder Eren
		</span>

		<span class="text-lg font-light text-base-content/70">
			polymath • stoic • human
		</span>

		<div class="flex gap-4 items-center">
			{#each socialLinks as link}
				<a class="btn btn-outline btn-accent" href={link.link}>
					<link.icon size={24} />
				</a>
			{/each}
		</div>
	</div>
</div>
