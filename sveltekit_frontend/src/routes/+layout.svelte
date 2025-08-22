<script lang="ts">
	import "../styles/app.css";

	let { children } = $props();
</script>

<div class="w-full h-dvh">
	{@render children()}
</div>
