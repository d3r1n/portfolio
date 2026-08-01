import re

_SLUG_STRIP_RE = re.compile(r"[^a-z0-9]+")

WORDS_PER_MINUTE = 200


def slugify(title: str) -> str:
	slug = _SLUG_STRIP_RE.sub("-", title.strip().lower()).strip("-")
	return slug or "post"


def estimate_reading_minutes(content: str) -> int:
	words = len(content.split())
	return max(1, words // WORDS_PER_MINUTE)
