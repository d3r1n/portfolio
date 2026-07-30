from fastapi import Request


def get_client_ip(request: Request) -> str:
	"""
	Safely extracts the real client IP address, accounting for the
	upstream reverse proxy layer (Caddy).
	"""
	# Check the standard header Caddy sets for the original client
	real_ip = request.headers.get("X-Real-IP")
	if real_ip:
		return real_ip

	# Fall back to X-Forwarded-For (can be a comma-separated list: client, proxy1, proxy2)
	forwarded_for = request.headers.get("X-Forwarded-For")
	if forwarded_for:
		# Grab the very first IP in the chain, which is the original client
		return forwarded_for.split(",")[0].strip()

	# local fallback if things aren't hitting the proxy during testing
	return request.client.host if request.client else "127.0.0.1"
