# TODO

- [ ] Implement browser sessions
    - [ ] need a database to store the session data (ip, device, location)
    - [ ] have a blacklist store
- [ ] Implement rate limiting
- [ ] Put frequent rate limiters to blacklisted ips
- [ ] add a scraper/ai deterer (anubis)
- [ ] mini analytics (basic information only for monitoring activity) \
       country, device platform (mobile, desktop, etc.), visit count, average interaction interval

---

- [x] What database to select?
    > requirements: lightweight, easily deployable for containers, SQL, easy to use, modern \
    > verdict: PostgreSQL

## Security setup

The backend now includes:

- Hybrid auth: session-cookie auth for browser traffic and personal access tokens for API clients.
- Role-based authorization (viewer/admin) for privileged endpoints.
- Postgres-backed rate limiting and automatic temporary blacklisting on repeated abuse.
- Admin blacklist management endpoints.

Set these env vars before running backend:

- `DB_URL` (Postgres URL, e.g. `postgres+asyncpg://...`)
