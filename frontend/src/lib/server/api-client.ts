/**
 * Server-only counterpart to `lib/viewer-auth.ts`, used by `load` functions.
 *
 * The browser talks to the backend through Caddy's `/api` proxy. Inside the
 * Docker network the SvelteKit server is a separate container from Caddy, so
 * it addresses the backend service directly instead (see `BACKEND_INTERNAL_URL`).
 *
 * Caches its own viewer JWT at module scope, mirroring the browser cache in
 * `viewer-auth.ts`. Sharing one token across concurrent requests is safe here
 * because the token only carries `{ role: "viewer", exp }` — no per-user or
 * per-request claims — so there's nothing to leak between visitors.
 */
import { env } from '$env/dynamic/private';
import { createClient, createConfig } from '$lib/api/client';
import { generateViewerSessionAuth, type ClientOptions } from '$lib/api';
import { expiryFromJwt } from '$lib/utils/jwt';

const EXPIRY_SKEW_MS = 30_000;

export const serverApiClient = createClient(
	createConfig<ClientOptions>({
		baseUrl: env.BACKEND_INTERNAL_URL || 'http://backend:5000',
		headers: env.INTERNAL_API_KEY
			? { 'X-Api-Key': env.INTERNAL_API_KEY }
			: undefined
	})
);

let cachedToken: { value: string; expiresAt: number } | null = null;
let pendingRefresh: Promise<string> | null = null;

async function refreshToken(): Promise<string> {
	const { data } = await generateViewerSessionAuth({
		client: serverApiClient,
		throwOnError: true
	});
	cachedToken = {
		value: data.access_token,
		expiresAt: expiryFromJwt(data.access_token)
	};
	return cachedToken.value;
}

async function getServerViewerToken(): Promise<string> {
	if (cachedToken && cachedToken.expiresAt - EXPIRY_SKEW_MS > Date.now()) {
		return cachedToken.value;
	}

	pendingRefresh ??= refreshToken().finally(() => (pendingRefresh = null));
	return pendingRefresh;
}

serverApiClient.setConfig({ auth: getServerViewerToken });
