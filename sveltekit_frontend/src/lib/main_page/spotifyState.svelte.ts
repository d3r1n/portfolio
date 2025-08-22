let trackIsPlaying: boolean = $state(false)

export function getTrackIsPlaying(): boolean {
    return trackIsPlaying;
}

export function setTrackIsPlaying(playing: boolean): void {
    trackIsPlaying = playing;
}