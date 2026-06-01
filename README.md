# Flask API Template

A minimal starting point for a Python JSON API built on **Flask**, **SQLAlchemy 2.x**, **Alembic**, and **Pydantic v2**, with interactive **OpenAPI docs** (Swagger UI / ReDoc) generated from the Pydantic schemas via **[Spectree](https://github.com/0b01001011/spectree)**. Ships with two interchangeable backends — **SQLite** (a single local file, zero setup, the default) and **MySQL** (networked) — selected by one env var. See [Choosing a database](#choosing-a-database). Swap the driver/URL for Postgres/etc. when a project outgrows them.

The endpoints in `app/main.py` (`/items`, `/manufacturers`) are scaffolding — delete them and replace with real domain models. The plumbing (app factory, engine, request-scoped session, Alembic wiring, settings) is the part worth keeping.

## Where to go

Once the server is up (`flask --app app run --debug`, default port `5000`):

| URL | What |
| --- | --- |
| [`/apidoc/swagger`](http://127.0.0.1:5000/apidoc/swagger) | **Swagger UI** — interactive docs, click-to-try requests. |
| [`/apidoc/redoc`](http://127.0.0.1:5000/apidoc/redoc) | **ReDoc** — clean, readable reference. |
| [`/apidoc/scalar`](http://127.0.0.1:5000/apidoc/scalar) | **Scalar** — modern docs UI, another flavor. |
| [`/apidoc/openapi.json`](http://127.0.0.1:5000/apidoc/openapi.json) | Raw **OpenAPI spec** (feed it to codegen, Postman, etc.). |
| [`/healthz`](http://127.0.0.1:5000/healthz) | Liveness check — `{"status": "ok"}`. |

All three doc UIs are generated from the same Pydantic schemas — pick whichever you like. See [Endpoints](#endpoints) for the API routes themselves.

## Layout

| Path | Purpose |
| --- | --- |
| `app/__init__.py` | App factory (`create_app`), blueprint registration, JSON error handlers, docs mount. |
| `app/main.py` | Routes (a Flask blueprint), each annotated with `@api.validate` for validation + docs. |
| `app/extensions.py` | The Spectree (`api`) instance that drives validation and the OpenAPI docs. |
| `app/database.py` | Engine, session factory, request-scoped `get_session`, `Base`. |
| `app/models.py` | SQLAlchemy ORM models. |
| `app/schemas.py` | Pydantic request/response models (validation + serialization). |
| `app/crud.py` | DB ops, kept separate from route handlers. |
| `app/config.py` | `pydantic-settings`, reads `.env`. |
| `alembic/` | Migration env + `versions/`. |
| `alembic.ini` | Alembic config (URL injected from `app.config`). |
| `requirements.txt` | Pinned dependencies. |
| `.env.example` | Copy to `.env` and edit. |

## Choosing a database

The backend is selected entirely by `DATABASE_URL` in `.env` — there is **one** switch and nothing else changes. The code adapts to the dialect automatically (engine pooling in `app/database.py`, batch migrations in `alembic/env.py`).

| | SQLite (default) | MySQL |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./flask_app.db` | `mysql+pymysql://root:root@127.0.0.1:3306/flask_app` |
| Driver | stdlib `sqlite3` (no install) | `PyMySQL` (in `requirements.txt`) |
| Setup | none — a file is created on first migration | install + run a MySQL server |
| Good for | quick local dev, tests, demos | shared/staging/prod-like environments |

**To switch backends, change that one line in `.env` and re-run `alembic upgrade head`.** The MySQL driver ships in `requirements.txt`, so no reinstall is needed. The two backends are separate stores — data does not carry over between them.

A few dialect details the template already handles for you:

- **SQLite path:** three slashes (`sqlite:///./flask_app.db`) is relative to the working directory; four slashes is an absolute path. `*.db` files are gitignored.
- **SQLite + Alembic:** SQLite can't `ALTER` most columns, so `alembic/env.py` turns on `render_as_batch` automatically when the URL is SQLite (Alembic rebuilds the table behind the scenes). MySQL alters in place.
- **Pooling:** `pool_pre_ping` is used for MySQL (drops stale network connections); SQLite skips it and sets `check_same_thread=False` so a connection can move across the dev server's request threads.

## Setup

### 1. Python venv

```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure the database

```shell
cp .env.example .env
```

`.env.example` ships with SQLite active and MySQL commented out. Pick one:

**Option A — SQLite (default; no server to install).** Nothing to edit — the copied `.env` already points at `sqlite:///./flask_app.db`, and the file is created when you run migrations. Skip to step 3.

**Option B — MySQL.** In `.env`, comment out the SQLite line and uncomment the MySQL one. Then install and start a local MySQL server:

```shell
brew install mysql
brew services start mysql
```

Create the database and (optionally) a dedicated user. The defaults in `.env.example` assume the root account with password `root` — fine for local dev, change for anything real:

```shell
mysql -uroot -e "CREATE DATABASE flask_app;"
mysql -uroot -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'root';"
```

Edit the MySQL `DATABASE_URL` in `.env` if your user/password/port differs. The format is:

```
mysql+pymysql://<user>:<password>@<host>:<port>/<database>
```

### 3. Run migrations

```shell
alembic upgrade head
```

This creates the `items` and `manufacturers` tables. The migrations are checked in under `alembic/versions/`.

To generate a new migration after editing models:

```shell
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

Revision IDs are zero-padded and sequential (`0001`, `0002`, `0003`, …) rather than Alembic's default random hex, so `ls alembic/versions/` reads in history order. This is handled by the `use_sequential_rev_ids` hook in `alembic/env.py` (it picks the next number above the highest existing numeric revision).

### 4. Run the API

```shell
flask --app app run --debug      # dev server with reloader, on http://127.0.0.1:5000
```

For a production-style run, use the bundled WSGI server (gunicorn):

```shell
gunicorn app:app                 # serves the create_app() instance from app/__init__.py
```

- Swagger UI: <http://127.0.0.1:5000/apidoc/swagger>
- ReDoc: <http://127.0.0.1:5000/apidoc/redoc>
- Scalar: <http://127.0.0.1:5000/apidoc/scalar>
- Raw OpenAPI spec: <http://127.0.0.1:5000/apidoc/openapi.json>
- Health: <http://127.0.0.1:5000/healthz>

The docs are generated by Spectree from the `@api.validate(...)` decorators on each route (`app/main.py`), which read the Pydantic schemas in `app/schemas.py`. Add a route + decorator and it shows up in Swagger automatically — the FastAPI experience, on Flask.

## Data model

Two tables with a foreign key, to illustrate a relationship:

- **`manufacturers`** — `id`, `name` (unique), `state` (2-letter code).
- **`items`** — `id`, `name` (unique), `description`, `price`, `created_at`, plus `manufacturer_id`, a non-null FK into `manufacturers`.

Every item belongs to one manufacturer. `GET /items` and `GET /items/{id}` return the item's columns **plus** the manufacturer nested in (`{..., "manufacturer": {"id", "name", "state"}}`), eager-loaded in `app/crud.py` to avoid N+1 queries. `POST /items` requires a valid `manufacturer_id` (400 if it doesn't exist); create manufacturers first via `POST /manufacturers`.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/healthz` | Liveness check (`{"status": "ok"}`). |
| `GET` | `/items` | List items (optional `?search=`). |
| `GET` | `/items/<id>` | One item, or 404. |
| `POST` | `/items` | Create an item (validates body; 400 on unknown manufacturer). |
| `GET` | `/manufacturers` | List manufacturers (optional `?search=`). |
| `GET` | `/manufacturers/<id>` | One manufacturer, or 404. |
| `POST` | `/manufacturers` | Create a manufacturer (validates body). |

Request validation (body + query) is handled by Spectree from the Pydantic schemas: a bad body or query param returns `422` with Pydantic's error list (Spectree's shape). Business errors raised with `abort()` (400/404) return `{"detail": "message"}`, wired up in `app/__init__.py`.

## Try it

A manufacturer must exist before an item can reference it:

```shell
# 1. create a manufacturer, note its "id" in the response
curl -X POST http://127.0.0.1:5000/manufacturers \
  -H 'Content-Type: application/json' \
  -d '{"name": "Acme Corp", "state": "CA"}'

# 2. create an item pointing at that manufacturer
curl -X POST http://127.0.0.1:5000/items \
  -H 'Content-Type: application/json' \
  -d '{"name": "Widget", "description": "a thing", "price": 9.99, "manufacturer_id": 1}'

curl http://127.0.0.1:5000/items     # each item includes its nested manufacturer
curl http://127.0.0.1:5000/items/1
curl 'http://127.0.0.1:5000/items?search=wid'   # case-insensitive name filter
```

Both list endpoints (`GET /items`, `GET /manufacturers`) take an optional `?search=` query param that does a case-insensitive `LIKE` on `name`. Literal `%` and `_` in the search are escaped, so they match themselves rather than acting as wildcards. Omitting it (or passing blank) returns everything.

Or just run `./seed.sh` (below), which does all of this for you.

### Seed sample data

`seed.sh` POSTs a few manufacturers and then items that reference them (so the foreign keys line up) to the running API, giving you data to look at. The API must be running and migrated first.

```shell
./seed.sh                                  # seeds http://127.0.0.1:5000 (Flask's default)
BASE_URL=http://127.0.0.1:8099 ./seed.sh   # different host/port
```

Because it goes through HTTP, it works identically against SQLite or MySQL. Edit the `items=(...)` array in the script to change what gets inserted.

## Using this as a starting point

1. Clone or copy this directory into a new repo.
2. **Rename the database** — see below. Don't leave it as `flask_app`, or every project off this template ends up sharing one database in your local MySQL.
3. Rename the `Item` model in `app/models.py` and the matching schemas/routes to your domain.
4. Drop the files in `alembic/versions/` and run `alembic revision --autogenerate -m "initial"` to regenerate against your new models.
5. Want Postgres instead? Replace `PyMySQL` with `psycopg[binary]` in `requirements.txt` and use `postgresql+psycopg://...` in `DATABASE_URL`. Nothing else changes.

### Renaming the database

> On **SQLite** there's nothing to rename: just point `DATABASE_URL` at a different filename (`sqlite:///./widgets.db`) and run `alembic upgrade head`. The steps below are for **MySQL**.

The template ships with a database named `flask_app`. For a real project, pick a name that matches the repo (e.g. `widgets`, `invoicing`) so your local MySQL doesn't turn into a junk drawer.

1. **Create the new database in MySQL:**

   ```shell
   mysql -uroot -proot -e "CREATE DATABASE widgets;"
   ```

2. **Update `.env`** — change the last path segment of `DATABASE_URL`:

   ```
   DATABASE_URL=mysql+pymysql://root:root@127.0.0.1:3306/widgets
   ```

3. **Update `.env.example`** to match, so anyone else cloning the repo gets the right default.

4. **Update the default in `app/config.py`** — the `database_url` field's default string is the fallback when `.env` is missing. Keep it consistent so the same name appears everywhere.

5. **Run migrations against the new database:**

   ```shell
   alembic upgrade head
   ```

6. **(Optional) Drop the old `flask_app` database** once you've confirmed everything works against the new one:

   ```shell
   mysql -uroot -proot -e "DROP DATABASE flask_app;"
   ```

That's it — three places to edit (`.env`, `.env.example`, `app/config.py`) plus the `CREATE DATABASE`. The Alembic config doesn't need touching; it reads the URL from `app.config` and follows along automatically.

## Managing dependencies

When you `pip install` something new during development, freeze the lockfile so the next clone reproduces your environment:

```shell
pip install <package>
pip freeze > requirements.txt
```

`pip freeze` writes every package in the active venv with exact versions. Make sure the venv is activated first (`source venv/bin/activate`) — otherwise you'll capture your system Python's packages instead.

To upgrade a pinned package later:

```shell
pip install --upgrade <package>
pip freeze > requirements.txt
```

## Design notes

- **App factory.** `app/__init__.py` builds the app in `create_app()` — registers the blueprint, wires the request-scoped session teardown, and installs JSON error handlers. A module-level `app = create_app()` is exposed so `flask --app app run` and `gunicorn app:app` both find it.
- **One settings object.** `app/config.py` is the single source for env-driven config; both the app and Alembic import it. Don't read env vars elsewhere. `DATABASE_URL` is the only knob that selects MySQL vs SQLite.
- **Sessions per request.** `get_session()` (in `app/database.py`) lazily opens one `Session` per request, stashed on Flask's `g`, and a `teardown_appcontext` handler closes it when the request ends. Don't share sessions across requests.
- **Dialect adaptation lives in two places.** `app/database.py` picks engine options per dialect (pooling vs `check_same_thread`) and turns on SQLite foreign-key enforcement (`PRAGMA foreign_keys=ON`, which SQLite otherwise ignores; MySQL/InnoDB enforces natively). `alembic/env.py` enables batch migrations for SQLite. Everything else — models, schemas, CRUD, routes — is backend-agnostic.
- **Eager-load relationships.** Reads of `items` use `selectinload(Item.manufacturer)` so the related row is fetched in one extra query rather than N. Hand-written migrations that alter a table use `op.batch_alter_table` for SQLite compatibility.
- **Named constraints via a naming convention.** `Base.metadata` sets a `naming_convention` (`app/database.py`) so every index/FK/unique/check constraint gets a deterministic name. SQLite's batch migrations *require* named constraints (autogenerate otherwise emits `None` and fails with "Constraint must have a name"), and named constraints can be dropped by the same name they were created under. Set this before your first migration on a new project.
- **Pydantic + Spectree for validation, serialization, and docs.** `app/schemas.py` defines request models (`*Create`, `SearchQuery`) and response models (`*Read`, `from_attributes=True`). The `@api.validate(...)` decorator on each route (Spectree, configured in `app/extensions.py`) validates incoming requests against those schemas, exposes validated input on `request.context`, and generates the OpenAPI spec + Swagger UI. Routes stay thin: read `request.context` → call `crud` → dump. Request validation failures surface as `422` automatically.
- **CRUD module, not fat routes.** `app/crud.py` keeps DB logic out of route handlers so routes stay thin and testable.
