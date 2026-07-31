from fastapi import Depends
from loguru import logger
from redis.asyncio import Redis

from portfolio.deps import get_redis

from ..database import Database


async def load_blacklists(db: Database, redis: Redis = Depends(get_redis)) -> None:
	# Load blacklists from the database and populate redis cache
	blacklists = await db.blacklist.all()

	# if failed to load blacklists, log the error and continue
	if not blacklists:
		logger.info("No blacklists found in the database to load into Redis cache.")
		return

	pipe = redis.pipeline()
	# Populate the redis cache with the loaded blacklists
	for bl in blacklists:
		pipe.set(bl.ip_address, bl.reason, ex=int((bl.expires_at - bl.created_at).total_seconds()))

	try:
		await pipe.execute()
		logger.info(f"Loaded {len(blacklists)} blacklists into Redis cache.")
	except Exception as e:
		logger.error(f"Failed to load blacklists into Redis cache: {e}")
