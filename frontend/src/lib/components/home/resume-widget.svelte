<script lang="ts">
	import { page } from '$app/state';
	import { ArrowUpRight, FileUser } from '@lucide/svelte';
	import cv_thumbnail from '$lib/assets/cv-thumbnail.png';

	// Whatever domain is currently serving the site (prod, staging, localhost,
	// ...), send visitors to its `cv.` subdomain.
	const cvUrl = $derived(
		`${page.url.protocol}//cv.${page.url.hostname.replace(/^www\./, '')}`
	);
</script>

<section class="grid grid-cols-4 gap-8">
	<!-- Left side  -->
	<div class="col-span-3 flex flex-col gap-4">
		<div class="flex flex-col gap-1">
			<span
				class="font-heading text-base-content/50 text-xs font-medium tracking-wider uppercase"
			>
				Resume
			</span>
			<h2 class="font-heading text-base-content text-lg font-semibold">
				Curriculum vitae
			</h2>
		</div>

		<div class="flex min-w-0 flex-1 flex-col items-start gap-4">
			<p class="font-body text-base-content/80 text-sm leading-relaxed">
				My CV is available online for your convenience. It provides a
				detailed summary of my professional experience, skills, and
				accomplishments. Feel free to explore it to learn more about my
				background and expertise.
			</p>
			<a
				href={cvUrl}
				target="_blank"
				rel="noopener noreferrer"
				class="btn btn-accent font-heading w-fit gap-2 rounded-sm"
			>
				<FileUser size={16} />
				View CV
				<ArrowUpRight size={14} />
			</a>
		</div>
	</div>

	<a
		href={cvUrl}
		target="_blank"
		rel="noopener noreferrer"
		class="group outline-base-content/10 hover:outline-base-content/20 items-center justify-center overflow-hidden rounded-sm outline-1 outline-offset-2 transition"
	>
		<img
			src={cv_thumbnail}
			alt="CV preview"
			class="h-full w-full object-cover opacity-80 transition group-hover:opacity-100"
		/>
	</a>
</section>
