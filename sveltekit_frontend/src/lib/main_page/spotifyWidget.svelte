<script lang="ts">
    import apiConfig from "@/api.const.json";
    import { setTrackIsPlaying } from "./spotifyState.svelte";

    import { browser } from "$app/environment";
    import { ArrowUpRight } from "@lucide/svelte";

    const CurrentlyPlayingUrl =
        apiConfig.spotify.baseUrl + apiConfig.spotify.currentlyPlayingUrl;

    const LastPlayedUrl =
        apiConfig.spotify.baseUrl + apiConfig.spotify.lastPlayedUrl;

    interface SpotifyTrack {
        name: string;
        track_url: string;
        album_name: string;
        album_image: string;
        duration_ms: number;
        progress_ms: number;
        is_playing: boolean;
        artists: Array<string>;
        artists_joined: string; // the api doesn't return this, it's for convinience
    }

    async function getCurrentlyPlaying() {
        let request = await fetch(CurrentlyPlayingUrl, {
            mode: "cors",
            headers: {
                "Content-Type": "application/json",
            },
        });

        return request;
    }

    async function getLastPlayed() {
        let request = await fetch(LastPlayedUrl, {
            mode: "cors",
            headers: {
                "Content-Type": "application/json",
            },
        });

        return request;
    }

    /*
        try getting the currently playing track if the response
        status is 204 No Content (actually anything other than 200 OK),
        get last played track 
    */
    async function getSpotifyTrack(): Promise<SpotifyTrack | null> {
        try {
            const currentlyPlayingResponse = await getCurrentlyPlaying();

            if (currentlyPlayingResponse.status == 200) {
                let currentlyPlayingData: SpotifyTrack =
                    await currentlyPlayingResponse.json();

                if (currentlyPlayingData.is_playing) {
                    currentlyPlayingData.artists_joined =
                        currentlyPlayingData.artists.join(", ");

                    // set state for sidebar to use
                    setTrackIsPlaying(true);

                    return currentlyPlayingData;
                }
            }

            const lastPlayedResponse = await getLastPlayed();
            let lastPlayedData: SpotifyTrack = await lastPlayedResponse.json();

            lastPlayedData.artists_joined = lastPlayedData.artists.join(", ");

            if (lastPlayedResponse.ok) {
                setTrackIsPlaying(false);
                return lastPlayedData;
            } else {
                return null;
            }
        } catch (error) {
            console.error("Error fetching track data:", error);
            return null;
        }
    }

    function shortenTextField(text: string, length: number = 20): string {
        if (text.length > length) {
            return text.substring(0, length) + "...";
        } else return text;
    }

    function displayTitle(text: string, length: number = 20): string {
        return text.length > length ? text : "";
    }
</script>

{#snippet skeleton()}
    <div class="flex gap-4 items-center self-start *:animate-pulse">
        <span class="w-32 aspect-square rounded-full bg-base-200"></span>

        <div class="flex flex-col gap-4 items-start justify-center">
            <span class="w-48 h-6 bg-base-200 rounded-lg"></span>
            <span class="w-32 h-4 bg-base-200 rounded-lg"></span>
            <span class="w-42 h-4 bg-base-200 rounded-lg"></span>
        </div>
    </div>
{/snippet}

{#await browser ? getSpotifyTrack() : Promise.resolve()}
    {@render skeleton()}
{:then track}
    {#if track == null}
        {@render skeleton()}
    {:else}
        <div class="flex gap-4 items-center self-start">
            <div class="relative w-32">
                <!-- Blur picture -->
                <img
                    src={track.album_image}
                    class="absolute w-full object-cover aspect-square rounded-full blur-sm opacity-80 z-1"
                    alt=""
                />

                <img
                    src={track.album_image}
                    alt={`${track.album_name} album by ${track.artists_joined}`}
                    title={`${track.album_name} album picture`}
                    class="relative w-full aspect-square object-cover z-2 rounded-full"
                />
            </div>

            <div class="flex flex-col gap-2 font-[Geist]">
                <a
                    href={track.track_url}
                    target="_blank"
                    class="tooltip text-base md:text-lg text-stone-900"
                    data-tip={displayTitle(track.name)}
                >
                    {shortenTextField(track.name)}
                    <ArrowUpRight
                        size="18"
                        color="var(--color-stone-900)"
                        class="inline align-baseline"
                    />
                </a>

                <span
                    class="tooltip text-sm md:text-base text-stone-600"
                    data-tip={displayTitle(track.artists_joined)}
                >
                    {shortenTextField(track.artists_joined)}
                </span>

                <span
                    class="tooltip text-xs md:text-sm text-stone-500"
                    data-tip={displayTitle(track.album_name)}
                >
                    {shortenTextField(track.album_name)}
                </span>
            </div>
        </div>
    {/if}
{/await}
