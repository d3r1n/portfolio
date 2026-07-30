from ..database import Database
from ..database.dto import ProjectData


def _placeholder_projects() -> list[ProjectData]:
	return [
		ProjectData(
			name="Project Atlas",
			description="A restrained portfolio and writing hub focused on content hierarchy and speed.",
			year="2026",
			status="Live",
			tags=["Svelte", "Tailwind", "DaisyUI"],
			href="https://github.com/d3r1n/portfolio",
			links=[{"label": "Repository", "href": "https://github.com/d3r1n/portfolio", "external": True}],
			accent="01",
		),
		ProjectData(
			name="Signal Room",
			description="A compact personal signal dashboard blending books, music, and context widgets.",
			year="2025",
			status="Ongoing",
			tags=["UX", "Data", "Frontend"],
			href="https://github.com/d3r1n",
			links=[{"label": "Profile", "href": "https://github.com/d3r1n", "external": True}],
			accent="02",
		),
	]


async def init_default_projects(db: Database):
	if await db.projects.has_any():
		# Projects already exist (either seeded before or added via the dashboard) — don't touch them.
		return

	await db.projects.create_many(_placeholder_projects())
