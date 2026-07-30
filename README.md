# Portfolio

Derin's personal website. A SvelteKit frontend renders a home page with live
widgets (currently-playing Spotify track, currently-reading book, current
location + weather, featured projects), backed by a FastAPI service that
talks to Spotify/Hardcover/OpenWeatherMap and stores its own data (projects,
location, admin accounts) in Postgres. Everything runs as a handful of
containers behind a Caddy reverse proxy.

## TODO

- (fill in as you go — open questions, half-finished features, etc.)

## Structure

```
portfolio/
├── frontend/        SvelteKit app (Svelte 5, Tailwind + DaisyUI, run via pnpm/Node)
├── backend/         FastAPI app (Python), talks to Postgres + Redis + 3rd-party APIs
├── compose.yaml      docker/podman compose file wiring all the containers together
├── Caddyfile         reverse proxy config — the single public entrypoint
└── Dockerfile.cron   tiny container that runs a nightly cleanup SQL job
```

The frontend and backend are independent projects that only communicate over
HTTP, through the reverse proxy. Neither imports code from the other — the
frontend's `src/lib/api/` folder is *generated* from the backend's OpenAPI
schema (see the Frontend section).

## Backend

Located in `backend/src/portfolio/`. It's a FastAPI app, started via
`uvicorn portfolio.main:app`. Folder-by-folder:

- **`main.py`** — creates the `FastAPI` app, registers all routers, sets up
  CORS, and defines the startup/shutdown sequence (the `lifespan` function):
  on boot it sets up logging, connects Redis, builds the third-party API
  clients, initializes the database and runs the seed services (see
  Services). On shutdown it closes all those connections cleanly. Also
  defines `/healthcheck` and a global error handler that turns any
  `UpstreamError` (a failed call to Spotify/Hardcover/OpenWeatherMap) into a
  uniform `502` JSON response.
- **`deps.py`** — small FastAPI "dependency" helpers (things you can `Depends()`
  on in a route to get config, Redis, or one of the API clients without
  constructing them yourself).
- **`core/`** — cross-cutting utilities with no business logic of their own:
  - `config.py` — all runtime configuration (DB URL, API keys, JWT settings,
    rate-limit numbers, admin credentials) loaded from environment variables
    via `pydantic-settings`, prefixed `BACKEND_`. Cached with `@lru_cache` so
    the whole app shares one `Config` instance.
  - `http.py` — pulls the real client IP out of a request, accounting for the
    fact that Caddy sits in front of the app (checks `X-Real-IP` /
    `X-Forwarded-For` before falling back to the raw socket address).
  - `logger.py` — configures `loguru` to log to stderr.
- **`database/`** — the persistence layer. This is the most involved part of
  the backend; see the dedicated **Database** section below.
- **`integrations/`** — HTTP clients for the three third-party services the
  site pulls data from:
  - `spotify/client.py` — refreshes an OAuth access token as needed, exposes
    currently-playing / last-played / top tracks / top artists.
  - `hardcover/client.py` — queries the Hardcover GraphQL API for the book
    currently being read.
  - `openweather/client.py` — resolves a location name to coordinates
    (geocoding) and fetches current weather for a coordinate.
  - `registry.py` — bundles all three clients plus one shared `aiohttp`
    session into an `Integrations` object, built once at startup and stashed
    on `app.state`. Every client raises a service-specific subclass of
    `UpstreamError` on failure, which `main.py`'s exception handler turns
    into a `502`.
- **`routers/`** — the actual HTTP endpoints, one file per feature area:
  - `auth.py` — issue viewer tokens, admin login, admin token verification.
  - `admin.py` — the admin dashboard API (CRUD for projects, set/read the
    current location). Everything here requires `require_admin`.
  - `books.py`, `spotify.py`, `location.py` — read-only endpoints the public
    home page widgets call. All require a viewer token.
  - `projects.py` — public "featured projects" listing.
  - All routers are collected into `all_routers` in `routers/__init__.py` and
    registered onto the app in `main.py`.
- **`security/`** — authentication, authorization and abuse protection. See
  the "How auth works" subsection below.
- **`schemas/`** — Pydantic models that define the *shape* of API
  requests/responses (as opposed to `database/dto.py`, which defines the
  shape of data crossing the database boundary — routers convert between the
  two).
- **`services/`** — one-shot setup routines run once at application startup
  (seeding the admin user, a default location, and placeholder projects). See
  the Services section below.
- **`tests/`** — pytest suite (`pytest-asyncio`), with `fakes.py` providing an
  in-memory SQLite stand-in for the Postgres-backed facade so tests don't need
  a real database.

### How auth works

There are **two separate token types**, because the site has two separate
audiences:

1. **Viewer tokens** (`security/jwt.py`) — every anonymous visitor's browser
   fetches one from `POST /auth/viewer-session` before the home page widgets
   can call anything. It's a short-lived (30 min), stateless JWT: the backend
   checks the signature and expiry only, no database lookup. Its only job is
   to stop random bots from hammering the widget endpoints directly — it's
   not really "identity", just a lightweight gate. `require_viewer` is the
   dependency that enforces it.
2. **Admin tokens** (`security/jwt.py` + `security/admin.py`) — issued on
   `POST /auth/admin-login` after checking a bcrypt password hash. Unlike
   viewer tokens, admin tokens are *whitelisted*: each login also creates a
   row in the `admin_sessions` table containing the token's unique ID (`jti`).
   `require_admin` decodes the JWT *and* checks that a matching, unexpired
   session row still exists — so revoking access (or just letting the session
   expire) actually takes effect immediately, rather than waiting out the
   JWT's own expiry. The token is delivered both as a JSON response and as an
   `httponly` cookie, and `require_admin` will accept it from either an
   `Authorization: Bearer` header or the cookie (the cookie path exists for
   Caddy's `forward_auth` check protecting `/db-admin`, see Deployment).

**Rate limiting** (`security/rate_limit.py`) is a Redis-backed fixed window:
for each `(client IP, route)` pair it increments a counter in a bucket that's
valid for the current 60-second window. Go over the configured limit and you
get a `429`; go *way* over (a multiplier of the limit) and the IP is written
to a Redis blacklist key (checked on every request) and durably logged in the
`blacklisted_ips` Postgres table for audit purposes — Redis is the fast path
that actually blocks requests, Postgres is just the paper trail. Trusted
internal callers (like Caddy's own health checks) can skip all of this by
sending a shared-secret `X-Api-Key` header.

## Frontend

Located in `frontend/`. A SvelteKit app using **Svelte 5** (runes syntax:
`$state`, `$derived`, `$props`), styled with **Tailwind CSS v4** + **DaisyUI**,
run and built with **pnpm** on Node (see `Dockerfile.dev`).

- **`src/routes/+layout.svelte`** — the root layout: loads global CSS and
  fonts, and imports `$lib/viewer-auth` once so the viewer-token flow (see
  below) is wired up before any widget can make a request.
- **`src/routes/+page.svelte`** / **`+page.server.ts`** — the home page:
  portrait/bio block, the music and book widgets, and a "featured projects"
  list. Featured projects and weather are server-rendered (`+page.server.ts`);
  the music and book widgets fetch client-side.
- **`src/routes/+error.svelte`** — site-wide error boundary.
- **`src/routes/derin/+page.svelte`** — currently an empty file (route
  exists, page not built yet).
- **`src/lib/components/`** — the UI pieces:
  - `navbar.svelte` — nav links plus a light/dark theme toggle animated with
    `animejs`.
  - `home/portrait.svelte` — the bio/photo header block.
  - `home/music-widget.svelte` — polls `/spotify/currently-playing` every 30s,
    falling back to `/spotify/last-played` if nothing's playing.
  - `home/book-widget.svelte` — polls `/books/currently-reading` every 60s.
  - `home/featured-projects.svelte` — receives its data from `+page.server.ts`.
  - `home/weather-widget.svelte` / `home/weather-content.svelte` — resolves
    the promise streamed in from `+page.server.ts`, then polls for live
    updates client-side.
  - `home/resume-widget.svelte` — links out to the CV's own subdomain.
- **`src/lib/server/api-client.ts`** — server-only API client used by `load`
  functions, since the SvelteKit server is a separate container from the one
  the browser reaches through Caddy's `/api` proxy.
- **`src/lib/api/`** — **generated code, not hand-written**. It's produced by
  `@hey-api/openapi-ts` (run via `pnpm run codegen` /
  `src/scripts/generate-api.ts`) reading the backend's OpenAPI schema, and
  gets wiped and regenerated on every dev/build run (`output.clean: true`).
  Never edit files in here directly.
- **`src/lib/viewer-auth.ts`** — lives *outside* `src/lib/api/` specifically
  because that folder gets deleted and regenerated. It registers a callback
  with the generated API client so that every API call automatically attaches
  a valid viewer JWT: it fetches one from the backend, caches it, and
  transparently refreshes it a little before it expires (so an in-flight
  request never races the token's expiry).

## Database

The backend uses **Postgres**, accessed through **Peewee's async ORM bridge**
(`playhouse.pwasyncio` — Peewee 4.x). The database code is organized in three
layers specifically so the ORM can be swapped later without touching any
router or service code:

```
database/
├── interface.py         Abstract contracts (Database + one Repository per aggregate)
├── dto.py                Pydantic models — the ONLY types allowed to cross the boundary
├── __init__.py           get_database() — the one line that picks the concrete backend
└── peewee_backend/
    ├── models.py          Peewee ORM model classes (private to this folder)
    ├── repositories.py    Implements the interfaces, using the Peewee models
    └── facade.py          Implements Database itself (connection lifecycle, sessions, transactions)
```

**Why the split exists:** nothing outside `portfolio.database` is allowed to
import a Peewee model directly. Routers, services and security code only ever
see `Database` (from `interface.py`) and DTOs (from `dto.py`). If the ORM or
even the database engine were ever swapped out, only `peewee_backend/` would
need to change — `get_database()` in `database/__init__.py` is the single
line that decides which concrete implementation gets used.

**The repository pattern:** each "aggregate" (a group of related tables that
should always be reasoned about together) gets its own repository class with
plain async methods — no query objects or ORM types leak out. There are four:

- `AdminRepository` — admin accounts and their login sessions.
- `ProjectRepository` — portfolio projects (the "featured projects" list).
- `LocationRepository` — the site owner's current location (just one row at a
  time — "get the latest" / "set a new one" / "clear").
- `BlacklistRepository` — the audit trail of rate-limit-blocked IPs.

The `Database` facade (implemented by `PeeweeDatabase` in `facade.py`)
exposes these four repositories as properties, plus connection lifecycle
methods: `init()` (create tables on startup), `close()` (release the pool on
shutdown), `session()` (hold one pooled connection for a block of code — used
per-request), and `transaction()` (wrap a block in a real DB transaction, so
either everything commits or nothing does).

**The five tables** (defined in `peewee_backend/models.py`), all with a UUID
primary key and `created_at`/`updated_at` timestamps:

- `admins` — one row per admin user (there's exactly one in practice — see
  Services). Stores a bcrypt password hash, never a plaintext password.
- `admin_sessions` — one row per *active admin login*. This is what makes
  admin JWTs revocable: `require_admin` (in `security/admin.py`) doesn't just
  trust the JWT's signature, it also checks that a session row with the
  token's `jti` still exists and hasn't expired. Foreign-keyed to `admins`
  with `on_delete="CASCADE"`, so deleting an admin wipes their sessions too.
  A nightly cron job (see Deployment) deletes expired rows here so the table
  doesn't grow forever.
- `project` — the portfolio projects shown on the home page and manageable
  from the admin dashboard. `tags` and `links` are stored as JSON columns
  (lists of strings / small objects) rather than separate tables, since they
  don't need to be queried independently.
- `current_location` — the site owner's current city, stored as
  `latitude`/`longitude` + a display name. Only the most-recently-created row
  is ever read (`get_current` orders by `created_at desc` and takes the
  first); old rows are cleared out when a new location is set (see Services).
- `blacklisted_ips` — durable record of IPs that got rate-limit-blocked
  (Redis holds the *live*, fast-to-check blacklist; this table is just the
  audit log so blocks survive a Redis restart and are inspectable later).

**One Peewee-specific quirk worth knowing:** `pwasyncio` connections are
*task-local* — each async task that wants to touch the database needs to
"enter" the database as an async context manager (`async with db:`) before
querying, which acquires a pooled connection for that task; entering again
while already inside is safe (it just reuses the same connection). That's
exactly what `Database.session()` does, and it's why `database/__init__.py`'s
`get_db()` FastAPI dependency wraps every request's handler in
`async with db.session(): yield db` — it guarantees a connection is checked
out for the lifetime of that one request.

You can inspect the actual data through **pgweb**, a web-based Postgres
browser exposed at `/db-admin` behind the Caddy proxy (see Deployment) — it's
gated behind the same admin-auth check as the dashboard API.

## Services

`services/` holds small one-shot functions that run once, in sequence, inside
a single database session, right after the schema is created at application
startup (`main.py`'s `lifespan`, via `db_init_services()` in
`services/__init__.py`):

1. **`initialize_admin.py`** — creates the one admin account from
   `BACKEND_ADMIN_*` env vars if it doesn't already exist (idempotent — safe
   to run on every restart).
2. **`init_location.py`** — resets and reseeds a placeholder current
   location ("Sackville, New Brunswick") inside a transaction, so a crash
   mid-reset can't leave the table empty. Meant to be overwritten later via
   the admin dashboard's "set current location" endpoint.
3. **`init_projects.py`** — seeds two placeholder projects, but **only if
   none exist yet** (`has_any()` check) — so it won't stomp on real projects
   you've added through the dashboard on later restarts.

## Deployment

Everything runs as containers, wired together by `compose.yaml` (run with
podman-compose in this environment, not Docker — see project setup). Services:

- **`caddy`** — the single public entrypoint (ports `8080`/`8443`). Routes
  requests based on path (see `Caddyfile`):
  - everything else → `frontend` (the Vite dev server, port 5173)
  - `/api/*` → `backend` (strips the `/api` prefix, forwards to port 5000)
  - `/db-admin/*` → `pgweb`, but only after a `forward_auth` sub-request to
    the backend's `/api/auth/admin-verify` succeeds (this is what makes the
    database browser admin-only — it reuses the exact same admin cookie/JWT
    check as the dashboard API, plus a shared internal API key so that
    forward-auth call itself skips rate limiting).
- **`frontend`** — builds from `frontend/Dockerfile.dev` (pnpm-based dev
  server with hot reload; source is bind-mounted for live editing). Also
  reaches the backend directly (`BACKEND_INTERNAL_URL`) for its own
  server-side `load` functions, bypassing Caddy.
- **`backend`** — builds from `backend/Dockerfile.dev` (installs deps with
  `uv`, runs `uvicorn --reload`; source is bind-mounted for live editing).
- **`database`** — plain `postgres:16-alpine` with a named volume so data
  survives container restarts.
- **`redis`** — plain `redis:7-alpine`, no volume — it's only ever used as a
  rate-limiter cache, so losing it on restart just resets counters/blacklists
  harmlessly.
- **`pgweb`** — web UI for browsing the Postgres database directly, only
  reachable through Caddy's `/db-admin` route (see above).
- **`cron-cleanup`** — builds from the root `Dockerfile.cron`: a minimal
  Alpine image running busybox `crond` with one job baked in at build time —
  every night at midnight, `DELETE FROM admin_sessions WHERE expires_at <=
  NOW()`, keeping that table from accumulating expired sessions forever.

All services share one Docker network (`portfolio-net`) and reach each other
by service name (e.g. the backend connects to Postgres at host `database`,
not `localhost`).
