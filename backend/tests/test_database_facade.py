"""Facade CRUD against an in-memory sqlite backend.

Running the same `PeeweeDatabase` facade on AsyncSqliteDatabase instead of
Postgres also proves the swappability point: nothing outside the facade
changes when the engine does.
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from playhouse.pwasyncio import AsyncSqliteDatabase

from portfolio.database.dto import BlogPostData, ProjectData
from portfolio.database.peewee_backend import models
from portfolio.database.peewee_backend.facade import PeeweeDatabase


@pytest.fixture
async def db():
	test_db = AsyncSqliteDatabase(":memory:")
	with test_db.bind_ctx(models.ALL_MODELS):
		facade = PeeweeDatabase(test_db)
		async with facade.session():
			await test_db.acreate_tables(models.ALL_MODELS)
			yield facade
		await test_db.close_pool()


def _project_data(name: str = "Test Project") -> ProjectData:
	return ProjectData(
		name=name,
		description="A test project.",
		year="2026",
		status="Live",
		tags=["python", "fastapi"],
		href="https://example.com",
		links=[{"label": "Repo", "href": "https://example.com", "external": True}],
		accent="01",
	)


async def test_project_crud_cycle(db: PeeweeDatabase):
	assert not await db.projects.has_any()

	created = await db.projects.create(_project_data())
	assert created.name == "Test Project"
	assert created.tags == ["python", "fastapi"]
	assert await db.projects.has_any()

	fetched = await db.projects.get(created.id)
	assert fetched is not None and fetched.id == created.id

	updated = await db.projects.update(created.id, {"status": "Archived"})
	assert updated is not None
	assert updated.status == "Archived"
	assert updated.name == "Test Project"  # untouched fields survive partial updates

	listed = await db.projects.list()
	assert [p.id for p in listed] == [created.id]

	assert await db.projects.update(uuid.uuid4(), {"status": "x"}) is None  # unknown id
	assert await db.projects.delete(created.id) is True
	assert await db.projects.delete(created.id) is False  # already gone
	assert not await db.projects.has_any()


async def test_project_seeding(db: PeeweeDatabase):
	await db.projects.create_many([_project_data("A"), _project_data("B")])
	assert [p.name for p in await db.projects.list()] == ["A", "B"]
	assert [p.name for p in await db.projects.list(limit=1)] == ["A"]


async def test_admin_sessions(db: PeeweeDatabase):
	admin = await db.admins.create(user="derin", email="derin@example.com", hashed_password="hash")
	assert (await db.admins.get_by_username("derin")) is not None
	assert (await db.admins.get_by_username("nobody")) is None

	valid = await db.admins.create_session(
		admin_id=admin.id, jti="valid-jti", expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
	)
	assert valid.admin_id == admin.id

	await db.admins.create_session(
		admin_id=admin.id, jti="expired-jti", expires_at=datetime.now(timezone.utc) - timedelta(hours=1)
	)

	assert (await db.admins.get_by_valid_session(admin.id, "valid-jti")) is not None
	assert (await db.admins.get_by_valid_session(admin.id, "expired-jti")) is None
	assert (await db.admins.get_by_valid_session(admin.id, "unknown-jti")) is None


async def test_current_location(db: PeeweeDatabase):
	assert await db.locations.get_current() is None

	await db.locations.set_current(location_name="Sackville, Canada", latitude=45.9, longitude=-64.4)
	second = await db.locations.set_current(location_name="Istanbul, Turkey", latitude=41.0, longitude=28.9)

	current = await db.locations.get_current()
	assert current is not None and current.id == second.id  # newest row wins

	assert await db.locations.clear() == 2
	assert await db.locations.get_current() is None


async def test_blacklist_upsert(db: PeeweeDatabase):
	expires = datetime.now(timezone.utc) + timedelta(minutes=30)
	await db.blacklist.upsert(ip_address="1.2.3.4", reason="first", expires_at=expires)
	# Second upsert for the same IP must update, not violate the unique constraint.
	await db.blacklist.upsert(ip_address="1.2.3.4", reason="second", expires_at=expires)

	row = await models.BlacklistedIp.aget(models.BlacklistedIp.ip_address == "1.2.3.4")
	assert row.reason == "second"


def _blog_post_data(title: str = "Hello World") -> BlogPostData:
	return BlogPostData(title=title, summary="A test post.", content="word " * 10)


async def test_blog_post_crud_cycle(db: PeeweeDatabase):
	created = await db.blog_posts.create(_blog_post_data(), slug="hello-world", reading_time_minutes=1)
	assert created.status == "draft"
	assert created.published_at is None

	fetched = await db.blog_posts.get_by_slug("hello-world")
	assert fetched is not None and fetched.id == created.id

	assert await db.blog_posts.slug_exists("hello-world") is True
	assert await db.blog_posts.slug_exists("nope") is False

	# drafts are excluded from the public feed
	assert await db.blog_posts.list_published() == []

	published = await db.blog_posts.set_status(created.id, "published")
	assert published is not None and published.status == "published"
	assert published.published_at is not None

	first_published_at = published.published_at
	republished = await db.blog_posts.set_status(created.id, "archived")
	assert republished is not None and republished.status == "archived"
	republished = await db.blog_posts.set_status(created.id, "published")
	assert republished is not None
	assert republished.published_at == first_published_at  # re-publish keeps the original date

	listed = await db.blog_posts.list_published()
	assert [p.id for p in listed] == [created.id]
	assert await db.blog_posts.count(status="published") == 1

	updated = await db.blog_posts.update(created.id, {"title": "New Title"})
	assert updated is not None and updated.title == "New Title"

	assert await db.blog_posts.delete(created.id) is True
	assert await db.blog_posts.get(created.id) is None
