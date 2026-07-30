from ..core.config import load_config
from ..core.logger import logger
from ..database import Database
from ..security import hash_password


async def init_admin_user(db: Database):
	config = load_config()

	# Check if an admin user already exists
	admin_user = await db.admins.get_by_username(config.admin.user)

	if not admin_user:
		# Create a new admin user
		await db.admins.create(
			user=config.admin.user, email=config.admin.email, hashed_password=hash_password(config.admin.password)
		)
		logger.info(f"Admin user '{config.admin.user}' created.")
	else:
		logger.info(f"Admin user '{config.admin.user}' already exists.")
