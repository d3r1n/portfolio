/** Reads the `exp` claim (seconds since epoch) off a JWT and returns it in milliseconds. */
export function expiryFromJwt(token: string): number {
	const payload = token.split('.')[1] ?? '';
	const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
	const json =
		typeof atob === 'function'
			? atob(base64)
			: Buffer.from(base64, 'base64').toString('utf-8');
	return (JSON.parse(json) as { exp: number }).exp * 1000;
}
