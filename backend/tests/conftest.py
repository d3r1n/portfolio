import os

# The app config loads eagerly at import time, so dummy settings must exist
# before any `portfolio` module is imported by a test.
_TEST_ENV = {
	"DB_URL": "postgresql+asyncpg://test:test@localhost:5432/test",
	"BACKEND_SPOTIFY__CLIENT_ID": "test-client-id",
	"BACKEND_SPOTIFY__CLIENT_SECRET": "test-client-secret",
	"BACKEND_SPOTIFY__REFRESH_TOKEN": "test-refresh-token",
	"BACKEND_HARDCOVER__USER_ID": "test-user",
	"BACKEND_HARDCOVER__API_TOKEN": "test-token",
	"BACKEND_OPENWEATHERMAP__API_KEY": "test-key",
	"BACKEND_ADMIN__USER": "testadmin",
	"BACKEND_ADMIN__PASSWORD": "testpassword",
	"BACKEND_ADMIN__EMAIL": "admin@example.com",
}

for key, value in _TEST_ENV.items():
	os.environ.setdefault(key, value)
