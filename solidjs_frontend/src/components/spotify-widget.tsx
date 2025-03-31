//@ts-ignore
import apiConfig from "@root/api.const.toml";

import { createResource, Suspense, Switch, Match } from "solid-js";

import { SkeletonRectangle, SkeletonLine } from "@/components/skeleton"

const CurrentlyPlayingUrl: string =
    apiConfig.spotify.baseUrl + apiConfig.spotify.currentlyPlayingUrl;

const LastPlayedUrl: string =
    apiConfig.spotify.baseUrl + apiConfig.spotify.lastPlayedUrl

interface Track {
    name: string,
    track_url: string
    album_name: string
    album_image: string
    duration_ms: number,
    progress_ms: number,
    is_playing: boolean,
    artists: Array<string>,
}

async function getCurrentlyPlaying(): Promise<Response> {
    let request = await fetch(CurrentlyPlayingUrl, {
        mode: "cors",
        headers: {
            "Content-Type": "application/json",
        },
    });

    return request
}

async function getLastPlayed(): Promise<Response> {
    let request = await fetch(LastPlayedUrl, {
        mode: "cors",
        headers: {
            "Content-Type": "application/json"
        },
    });

    return request
}

/*
    try getting the currently playing track if the response
    status is 204 No Content (actually anything other than 200 OK),
    get last played track 
*/
async function getTrack(): Promise<Track | null> {
    try {
        const currentlyPlayingResponse = await getCurrentlyPlaying();

        if (currentlyPlayingResponse.status == 200) {
            const currentlyPlayingData = await currentlyPlayingResponse.json();

            if (currentlyPlayingData.is_playing) {
                return currentlyPlayingData
            }
        }

        const lastPlayedResponse = await getLastPlayed();
        const lastPlayedData = await lastPlayedResponse.json();


        return lastPlayedResponse.ok ? lastPlayedData : null;
    } catch (error) {
        console.error("Error fetching track data:", error);
        return null;
    }
}


function SpotifyWidgetSkeleton() {
    return (
        <div class="w-full h-full gap-4 p-4 flex items-center box-border">
            <SkeletonRectangle classExtra={["w-2/5 aspect-square", "bg-neutral-300"]} />

            <div class="skeleton-lines w-1/2 h-full flex flex-col justify-end gap-4 ">
                <SkeletonLine classExtra={["w-3/5", "h-4", "bg-neutral-300"]} />
                <SkeletonLine />
                <SkeletonLine classExtra={["w-4/5", "h-4", "bg-neutral-300"]} />
            </div>
        </div>
    )
}

export default function SpotifyWidget(props: { classExtra?: Array<string> }) {
    const [trackData] = createResource(getTrack);

    if (!props.classExtra) {
        props.classExtra = []
    }

    return (
        <div class={["spotify-widget flex justify-center items-center w-full h-full bg-neutral-200 rounded-md box-border shadow-md", ...props.classExtra].join(" ")}>
            <Suspense fallback={<SpotifyWidgetSkeleton />}>
                <Switch>
                    <Match when={trackData.loading || !trackData()}>
                        <SpotifyWidgetSkeleton />
                    </Match>

                    <Match when={trackData()}>
                        {(resolvedTrack) => {
                            const track = resolvedTrack();

                            if (!track) return null; // Extra safety check

                            return (
                                <div class="spotify-widget-container w-full h-full p-4 flex gap-4 items-center box-border">
                                    <img src={track.album_image} alt="" class="w-2/5 aspect-square rounded-md" />

                                    <div class="spotify-widget-details h-full flex flex-col justify-end gap-1 text-neutral-900">
                                        <span class="text-sm font-[Inter] text-neutral-500">
                                            {track.is_playing ? "Now playing" : "Last played"}
                                        </span>

                                        <span class="text-xl font-[Inter] font-medium">
                                            {track.name}
                                        </span>

                                        <span class="text-base font-[Inter] text-neutral-600">
                                            {track.artists[0]}
                                        </span>
                                    </div>
                                </div>
                            );
                        }}
                    </Match>
                </Switch>
            </Suspense>
        </div>
    );
}
