<script lang="ts">
	import {
		CircleUser,
		DraftingCompass,
		LayoutDashboard,
		MessageCircle,
		Moon,
		Newspaper,
		Rocket,
		Sun,
		type Icon as IconType,
	} from "@lucide/svelte";

	type NavItem = {
		name: string;
		href: string;
		icon: typeof IconType;
	};

	const navItems: NavItem[] = [
		{ name: "Me", href: "#me", icon: CircleUser },
		{ name: "My Work", href: "#work", icon: DraftingCompass },
		{ name: "Writings", href: "#writings", icon: Newspaper },
		{ name: "Let's Talk", href: "#lets-talk", icon: MessageCircle },
		{ name: "Stuff", href: "#stuff", icon: LayoutDashboard },
	];
</script>

<div id="navbar" class="navbar px-4 shadow-sm dark:shadow-none">
	<a class="navbar-start flex items-center" href="/">
		<Rocket size={24} class="btn btn-ghost btn-square p-1 stroke-sky-500" />
	</a>

	<div class="navbar-center flex gap-4 items-center">
		{#each navItems as item}
			<a
				aria-label={item.name}
				class="btn btn-outline btn-md btn-secondary text-base-content"
				href={item.href}
			>
				<item.icon size={24} />

				{item.name}
			</a>
		{/each}
	</div>

	<div class="navbar-end">
		<label class="swap swap-rotate relative">
			<!-- this hidden checkbox controls the state -->
			<input type="checkbox" class="theme-controller" value="wireframe" />

			<Sun size={24} class="swap-on z-10 size-8 stroke-current" />

			<Moon
				size={24}
				class="swap-off absolute t-0 l-0 z-20 size-8 stroke-current"
			/>
		</label>
	</div>
</div>
