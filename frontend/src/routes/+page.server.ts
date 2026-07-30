import { currentLocationAndWeather, featuredProjects } from '$lib/api';
import { serverApiClient } from '$lib/server/api-client';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
	// Cheap DB read — worth blocking the initial render on.
	const { data: projects, error: projectsError } = await featuredProjects({
		client: serverApiClient,
		query: { limit: 2 }
	});
	if (projectsError) {
		console.error('Error fetching featured projects:', projectsError);
	}

	// Live upstream call to OpenWeatherMap — streamed in separately so it
	// never blocks the rest of the page from rendering.
	const weather = currentLocationAndWeather({ client: serverApiClient }).then(
		({ data, error }) => {
			if (error) console.error('Error fetching weather data:', error);
			return data ?? null;
		}
	);

	return {
		projects: projects ?? null,
		weather
	};
};
