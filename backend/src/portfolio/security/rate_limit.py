import time
from datetime import datetime, timedelta, timezone
from secrets import compare_digest

from fastapi import Depends, HTTPException, Request, status
from loguru import logger
from redis.asyncio import Redis

from ..core.config import load_config
from ..core.http import get_client_ip
from ..database import Database, get_database
from ..deps import get_redis

config = load_config()

WINDOW_SECONDS = 60


def _endpoint_label(request: Request) -> str:
	"""Templated route path (e.g. "GET /spotify/top/{type}") so all callers of the
	same route share one bucket, regardless of the concrete path params they used."""
	route = request.scope.get("route")
	path = route.path if route is not None else request.url.path
	return f"{request.method} {path}"


def _blacklist_key(ip: str) -> str:
	return f"blacklist:{ip}"


def _is_internal_caller(api_key: str | None) -> bool:
	"""Constant-time check against the configured internal key, so a slow string
	compare can't leak how much of the secret an attacker's guess got right."""
	internal_key = config.security.internal_api_key
	if not internal_key or not api_key:
		return False
	return compare_digest(api_key, internal_key)


async def _persist_blacklist(db: Database, ip: str, reason: str, expires_at: datetime) -> None:
	"""Durable record of the block, so it survives a Redis restart and is auditable later.
	Redis remains the source of truth for *enforcement* — this is just the paper trail."""
	# Short-lived connection scope: the limiter's hot path never touches the
	# database, so we only borrow a connection for this one write.
	async with db.session():
		await db.blacklist.upsert(ip_address=ip, reason=reason, expires_at=expires_at)


def rate_limit(requests_per_minute: int | None = None):
	"""
	Dependency factory for a per-endpoint rate limiter, backed by a Redis fixed window.

	Usage:
		router = APIRouter(dependencies=[Depends(rate_limit())])                # router-wide default
		@router.get("/expensive", dependencies=[Depends(rate_limit(10))])       # tighter override

	Every request's allow/deny decision is a couple of Redis ops (INCR + EXPIRE on a
	`ip:endpoint:<60s bucket>` key) — no database round trip on the hot path, so normal
	and even heavy traffic never touches Postgres. Postgres is only written to when a
	request actually gets rejected or an IP crosses into a blacklist, keeping the audit
	trail limited to things worth auditing rather than a row per request.

	Trusted internal callers (service-to-service) can skip the limiter entirely by
	sending `X-Api-Key` set to `security.internal_api_key` — see `_is_internal_caller`.
	"""
	limit = requests_per_minute or config.security.default_rate_limit_per_minute
	blacklist_threshold = limit * config.security.auto_blacklist_multiplier

	async def dependency(
		request: Request,
		redis: Redis = Depends(get_redis),
	) -> None:
		ip = get_client_ip(request)
		endpoint = _endpoint_label(request)
		api_key = request.headers.get("X-Api-Key")

		if _is_internal_caller(api_key):
			return

		if await redis.exists(_blacklist_key(ip)):
			raise HTTPException(
				status_code=status.HTTP_429_TOO_MANY_REQUESTS,
				detail="IP temporarily blocked due to abusive request rate",
			)

		# Wall-clock aligned window: e.g. 12:00:00-12:00:59 is one bucket, key changes every
		# minute on its own, so the EXPIRE below is just memory hygiene, not load-bearing.
		bucket = int(time.time() // WINDOW_SECONDS)
		window_key = f"ratelimit:{ip}:{endpoint}:{bucket}"

		async with redis.pipeline(transaction=True) as pipe:
			pipe.incr(window_key)
			pipe.expire(window_key, WINDOW_SECONDS + 5)
			count, _ = await pipe.execute()

		if count <= limit:
			return

		# Past the limit — log the rejection
		logger.warning(f"Rate limit exceeded for {ip} on {endpoint}: {count}/{limit}/min")

		if count > blacklist_threshold:
			expires_at = datetime.now(timezone.utc) + timedelta(minutes=config.security.auto_blacklist_minutes)
			await redis.set(_blacklist_key(ip), "1", ex=config.security.auto_blacklist_minutes * 60)
			await _persist_blacklist(
				get_database(), ip, reason=f"Exceeded {limit}/min on {endpoint}", expires_at=expires_at
			)
			raise HTTPException(
				status_code=status.HTTP_429_TOO_MANY_REQUESTS,
				detail="Too many requests — IP has been temporarily blocked",
			)

		raise HTTPException(
			status_code=status.HTTP_429_TOO_MANY_REQUESTS,
			detail="Rate limit exceeded",
			headers={"Retry-After": str(WINDOW_SECONDS)},
		)

	return dependency
