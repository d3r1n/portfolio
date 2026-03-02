<script lang="ts">
	import { siDevdotto } from "simple-icons";

	let { size = 24 } = $props();

	// We inject the SVG, but we need to make sure the internal
	// SVG element obeys the parent's dimensions.
</script>

<div
	class="icon-container inline-block"
	style="width: {size}px; height: {size}px;"
>
	{@html siDevdotto.svg}
</div>

<style>
	/* This ensures the injected <svg> fills the container */
	.icon-container :global(svg) {
		width: 100%;
		height: 100%;
		fill: currentColor;
	}
</style>
