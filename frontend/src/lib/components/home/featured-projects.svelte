<script lang="ts">
	import { onMount } from 'svelte';
	import {
		getFeaturedProjects,
		type FeaturedProject
	} from '$lib/api/client';

	let { limit = 2, class: className = '' } = $props<{
		projects?: FeaturedProject[];
		limit?: number;
		class?: string;
	}>();

	let projects = $state<FeaturedProject[] | null>(null);
	let visibleProjects = $derived(projects ? projects.slice(0, limit) : []);

	onMount(async () => {
		projects = await getFeaturedProjects(limit);
	});
</script>

{#if projects}
	<section class={`${className} flex flex-col gap-4 rounded-sm p-3`}>
		<div class="flex items-end justify-between gap-4">
			<div class="flex flex-col gap-1">
				<span
					class="font-heading text-base-content/50 text-xs font-medium tracking-wider uppercase"
				>
					Selected work
				</span>
				<h2
					class="font-heading text-base-content text-lg font-semibold"
				>
					Featured projects
				</h2>
			</div>

			<span class="font-body text-base-content/50 text-xs">
				{visibleProjects.length} projects
			</span>
		</div>

		<div class="grid gap-3">
			{#each visibleProjects as project, index}
				<article
					class="outline-base-content/10 bg-base-100/40 hover:bg-base-content/5 grid gap-4 rounded-sm p-4 outline-2 transition sm:grid-cols-[auto,1fr]"
				>
					<div
						class="border-base-content/10 bg-base-content/5 flex h-14 w-14 items-center justify-center rounded-sm border text-xs font-semibold"
					>
						{project.accent ?? String(index + 1).padStart(2, '0')}
					</div>

					<div class="flex min-w-0 flex-col gap-3">
						<div
							class="flex flex-wrap items-start justify-between gap-2"
						>
							<div class="min-w-0">
								<h3
									class="font-heading text-base-content truncate text-base font-semibold"
								>
									{project.name}
								</h3>
								<p
									class="font-body text-base-content/70 mt-1 text-sm leading-relaxed"
								>
									{project.description}
								</p>
							</div>

							<div
								class="font-heading flex shrink-0 items-center gap-2"
							>
								{#if project.year}
									<span class="badge badge-ghost"
										>{project.year}</span
									>
								{/if}
								{#if project.status}
									<span class="badge badge-success badge-soft"
										>{project.status}</span
									>
								{/if}
							</div>
						</div>

						<div class="flex flex-wrap gap-2">
							{#each project.tags ?? [] as tag}
								<span class="badge badge-outline badge-sm"
									>{tag}</span
								>
							{/each}
						</div>

						<div class="font-heading flex flex-wrap gap-2">
							{#if project.href}
								<a
									href={project.href}
									class="btn btn-sm btn-neutral"
								>
									Project
								</a>
							{/if}

							{#each project.links ?? [] as link}
								<a
									href={link.href}
									target={link.external === false
										? undefined
										: '_blank'}
									rel={link.external === false
										? undefined
										: 'noopener noreferrer'}
									class="btn btn-sm btn-outline btn-neutral"
								>
									{link.label}
								</a>
							{/each}
						</div>
					</div>
				</article>
			{/each}
		</div>
	</section>
{/if}
