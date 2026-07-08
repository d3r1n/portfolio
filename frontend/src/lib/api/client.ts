import type { components } from './schema';

const API_BASE = '/api';

type ApiErrorPayload = {
	error?: string;
	message?: string;
};

export type Track = components['schemas']['Track'];
export type HardcoverBook = components['schemas']['HardcoverBook'];
export type FeaturedProject = components['schemas']['FeaturedProject'];
export type TopType = 'artists' | 'tracks';

async function parseErrorMessage(response: Response): Promise<string> {
	try {
		const payload = (await response.json()) as ApiErrorPayload;
		return payload.message ?? payload.error ?? `Request failed with status ${response.status}`;
	} catch {
		return `Request failed with status ${response.status}`;
	}
}

async function getJsonOrNull<T>(path: string): Promise<T | null> {
	const response = await fetch(`${API_BASE}${path}`);
	if (response.status === 204) return null;
	if (!response.ok) {
		throw new Error(await parseErrorMessage(response));
	}
	return (await response.json()) as T;
}

export function getCurrentlyPlayingTrack(): Promise<Track | null> {
	return getJsonOrNull<Track>('/spotify/currently-playing');
}

export function getLastPlayedTrack(): Promise<Track | null> {
	return getJsonOrNull<Track>('/spotify/last-played');
}

export function getCurrentlyReadingBook(): Promise<HardcoverBook | null> {
	return getJsonOrNull<HardcoverBook>('/books/currently-reading');
}

export function getFeaturedProjects(limit = 2): Promise<FeaturedProject[] | null> {
	return getJsonOrNull<FeaturedProject[]>(`/projects/featured?limit=${limit}`);
}

export async function getTopSpotifyType(
	type: TopType,
	limit = 10
): Promise<Track[] | components['schemas']['TopArtist'][] | null> {
	return getJsonOrNull<Track[] | components['schemas']['TopArtist'][]>(
		`/spotify/top/${type}?limit=${limit}`
	);
}
