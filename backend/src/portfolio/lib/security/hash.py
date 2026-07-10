"""bcrypt stores the salt as part of the hash, so it doesn't need to be stored separately.
The salt is generated randomly for each password, which makes it more secure against rainbow table attacks.
"""

import bcrypt


def hash_password(password: str) -> str:
	"""Hashes a plain text password using a secure, randomly generated salt."""
	password_bytes = password.encode("utf-8")
	salt = bcrypt.gensalt()
	return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
	"""Verifies that a plain text password matches the stored database hash."""
	return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
