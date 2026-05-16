<script lang="ts">
	import { TriangleAlert } from '@lucide/svelte';

	let displayAlert = $state(false);
	let copied = $state(false); // Toggle state

	function copyEmailEvent() {
		if (!navigator.clipboard || copied) return; // Prevent spamming while success is active

		// TODO: Make those satisfying success animations for copying the email
		// using animejs
		navigator.clipboard
			.writeText('me@derineren.net')
			.then(() => {
				copied = true;
				setTimeout(() => (copied = false), 2000);
			})
			.catch(() => {
				displayAlert = true;
				setTimeout(() => (displayAlert = false), 2000);
			});
	}
</script>

<svelte:window
	onkeydown={(e) => e.key.toLowerCase() === 'c' && copyEmailEvent()}
/>

{#if displayAlert}
	<div class="toast toast-bottom toast-end">
		<div class="alert alert-warning flex items-center gap-2">
			<TriangleAlert />
			<span> Couldn't copy email to clipboard </span>
		</div>
	</div>
{/if}

<div class="flex flex-col gap-4">
	<div
		class="font-heading text-base-content/60 flex h-10 items-center gap-2 rounded-md p-2"
		id="copy-email"
	>
		{#if !copied}
			<span>press</span>
			<kbd class="kbd kbd-sm">C</kbd>
			<span>to copy my email</span>
		{:else}
			<span>me[at]derineren.net copied to clipboard.</span>
		{/if}
	</div>

	<p class="font-body text-base-content text-base tracking-wide">
		Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus
		convallis suscipit suscipit. Pellentesque tempus, tortor ac blandit
		elementum, tortor velit dignissim velit, id placerat nunc arcu ac est.
		Sed non nisl interdum turpis iaculis aliquet. Nulla facilisi. Mauris et
		semper purus. In erat nisl, pulvinar vel efficitur vitae, sagittis a
		enim. Aliquam libero elit, sodales congue augue ac, sodales posuere
		lectus. Aliquam sit amet augue non nisi venenatis euismod in id felis.
		Duis hendrerit, nisl id fermentum venenatis, urna metus mollis nisi, ut
		eleifend nunc lorem eu quam. Sed at augue nec massa sagittis sodales in
		non ante. Aenean quis varius sem, sed aliquam enim. Nam elementum massa
		nisi, sed placerat urna aliquet non. Aliquam tempus euismod est, id
		egestas est elementum at. Fusce sem risus, placerat eu enim elementum,
		ullamcorper pulvinar dolor.
	</p>
</div>
