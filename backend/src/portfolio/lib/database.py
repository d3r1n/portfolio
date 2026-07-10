from collections.abc import AsyncGenerator

from loguru import logger
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from .util.config import load_config

DATABASE_URL = load_config().db_url

# if load_config().deployment_mode == "DEV":
# 	echo = True
# else:
# 	echo = False
# TODO: solve the logging issue with SQLAlchemy and loguru, also uvicorn
echo = False  # sqlalchemy messes up the logs with repeated statements, loguru intercepts


# We use echo=False in production to keep logs clean, True can be used for debugging SQL.
async_engine = create_async_engine(DATABASE_URL, echo=echo, future=True)

async_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
	bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


# yield an async session for dependency injection in FastAPI routes
# after the request is done, the session will be closed automatically
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
	async with async_session_maker() as session:
		yield session


async def init_admin_user():
	from .security import Admin, hash_password
	from .util.config import load_config

	config = load_config()

	async with async_session_maker() as session:
		# Check if an admin user already exists
		existing_admin = await session.exec(select(Admin).where(Admin.user == config.admin.user))
		admin_user = existing_admin.first()

		if not admin_user:
			# Create a new admin user
			new_admin = Admin(
				user=config.admin.user, email=config.admin.email, hashed_password=hash_password(config.admin.password)
			)
			session.add(new_admin)
			await session.commit()
			logger.info(f"Admin user '{config.admin.user}' created.")
		else:
			logger.info(f"Admin user '{config.admin.user}' already exists.")


# Helper function to initialize database tables (useful for development)
async def init_db():
	async with async_engine.begin() as conn:
		# This creates tables defined by SQLModel.metadata if they do not exist
		await conn.run_sync(SQLModel.metadata.create_all)

	await init_admin_user()
