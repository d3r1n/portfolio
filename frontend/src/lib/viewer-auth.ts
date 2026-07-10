/**
 * Bootstraps viewer authentication for the generated API client.
 *
 * The backend gates every widget endpoint behind a short-lived, stateless
 * JWT (`POST /auth/viewer-session`, ~30 min lifetime). Rather than have every
 * call site fetch and attach that token, we register a single `auth`
 * callback on the shared client — the generated SDK functions already
 * declare `security: [{ scheme: 'bearer' }]`, so hey-api invokes this
 * callback automatically and attaches `Authorization: Bearer <token>`.
 *
 * This file intentionally lives outside `src/lib/api/`: hey-api regenerates
 * that directory from scratch (`output.clean: true`) on every dev/build run,
 * so anything hand-written in there would be deleted.
 */
import { client } from '$lib/api/client.gen';
import { generateViewerSessionAuth } from '$lib/api';

// Refresh a little ahead of expiry so an in-flight request never races the server's clock.
const EXPIRY_SKEW_MS = 30_000;

let cachedToken: { value: string; expiresAt: number } | null = null;
let pendingRefresh: Promise<string> | null = null;

/** Reads `exp` off the JWT itself so our cache mirrors the server's expiry exactly. */
function expiryFromJwt(token: string): number {
	const payload = token.split('.')[1] ?? '';
	const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
	const json =
		typeof atob === 'function'
			? atob(base64)
			: Buffer.from(base64, 'base64').toString('utf-8');
	return (JSON.parse(json) as { exp: number }).exp * 1000;
}

async function refreshToken(): Promise<string> {
	const { data } = await generateViewerSessionAuth({
		throwOnError: true
	});
	cachedToken = {
		value: data.access_token,
		expiresAt: expiryFromJwt(data.access_token)
	};
	return cachedToken.value;
}

async function getViewerToken(): Promise<string> {
	if (cachedToken && cachedToken.expiresAt - EXPIRY_SKEW_MS > Date.now()) {
		return cachedToken.value;
	}

	// Coalesce concurrent callers (e.g. multiple widgets mounting at once) into one request.
	pendingRefresh ??= refreshToken().finally(() => (pendingRefresh = null));
	return pendingRefresh;
}

client.setConfig({ auth: getViewerToken });
