<script lang="ts">
    import { getTrackIsPlaying } from "./spotifyState.svelte";
    import SpotifyWidget from "./spotifyWidget.svelte";

    import { siGithub, siDevdotto } from "simple-icons";
    import {
        Disc,
        Disc3,
        Hammer,
        Linkedin,
        MessageCircle,
        Sprout,
        type Icon as IconType,
    } from "@lucide/svelte";
    import { animate } from "animejs";

    type NavItem = {
        name: string;
        href: string;
        icon: typeof IconType;
    };

    const navItems: NavItem[] = [
        { name: "Origins", href: "#origins", icon: Sprout },
        { name: "My Work", href: "#mywork", icon: Hammer },
        { name: "Let's Talk", href: "#letstalk", icon: MessageCircle },
    ];

    function rotateDiscAnimation(node: HTMLElement) {
        animate(node, {
            rotate: "1turn",
            duration: 2000,
            ease: "linear",
            loop: true,
        });
    }
</script>

<div
    id="sidebar-widget"
    class="flex flex-col items-center justify-center gap-4 p-4 w-9/10 md:max-w-128 outline-1 outline-base-200 rounded-md"
>
    <div class="flex gap-4 items-center justify-around w-full">
        <img
            src="https://cdn.britannica.com/67/148167-050-F596E6F2/Marcus-Aurelius-statue-Rome-Piazza-del-Campidoglio.jpg"
            alt=""
            class="object-cover rounded-full w-1/3 md:max-w-32 aspect-square"
        />

        <div class="flex flex-col gap-4 max-w-2/3">
            <span
                class="font-[Geist] font-bold tracking-wide text-2xl text-base-content"
            >
                Derin Onder Eren
            </span>

            <span class="font-[Geist] text-base text-base-content/50">
                polymath • stoic • human
            </span>
        </div>
    </div>

    <div
        class="flex items-center justify-between gap-8 mb-4 w-full font-[Geist]"
    >
        <span
            class="btn btn-outline btn-primary flex-1 flex items-center justify-center py-6 *:size-6 *:fill-primary hover:*:fill-primary-content"
        >
            {@html siGithub.svg}
            GitHub
        </span>
        <span
            class="btn btn-outline btn-primary flex-1 flex items-center justify-center py-6 *:size-6 *:stroke-primary hover:*:stroke-primary-content"
        >
            <Linkedin />
            LinkedIn
        </span>
        <span
            class="btn btn-outline btn-primary flex-1 flex items-center justify-center py-6 *:size-6 *:fill-primary hover:*:fill-primary-content"
        >
            {@html siDevdotto.svg}
            Dev.to
        </span>
    </div>

    <div class="flex flex-col gap-8 w-full">
        {#each navItems as item}
            <a
                href={item.href}
                class="link-secondary link-hover flex-1 flex items-center justify-start gap-4 p-2 outline-1 outline-base-300 rounded-lg font-[Geist]"
            >
                <item.icon size={24} color="var(--color-secondary)" />

                {item.name}
            </a>
        {/each}
    </div>

    <span class="divider"></span>

    <span
        class="flex items-center gap-4 self-start font-[Geist] text-base text-base-content/50"
    >
        {#if getTrackIsPlaying()}
            <span use:rotateDiscAnimation>
                <Disc3 />
            </span>

            Listening to...
        {:else}
            <Disc />

            Recently played...
        {/if}
    </span>

    <SpotifyWidget />
</div>
