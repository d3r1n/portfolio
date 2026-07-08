from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from ..deps import get_config

DATABASE_URL = get_config().db_url

if get_config().deployment_mode == "DEV":
	echo = True
else:
	echo = False

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


# Helper function to initialize database tables (useful for development)
async def init_db():
	async with async_engine.begin() as conn:
		# This creates tables defined by SQLModel.metadata if they do not exist
		await conn.run_sync(SQLModel.metadata.create_all)
